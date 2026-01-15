"""
Main Pipeline - Motorsport Digest
Orchestre tout le processus de génération du digest hebdomadaire
"""

from datetime import datetime, timedelta
import pandas as pd
import sys
import os
import importlib

# Importer modules locaux
from rss_aggregator import fetch_rss_feeds, filter_recent_articles, save_to_database
from article_extractor import extract_batch_articles

# FORCER LE RELOAD du scorer pour éviter cache Python
import article_scorer
importlib.reload(article_scorer)
from article_scorer import rank_articles, get_top_articles

from article_deduplicator import deduplicate_articles
from ai_summarizer import estimate_cost
from bilingual_summarizer import summarize_batch_bilingual
from bilingual_web_generator import generate_bilingual_html


def print_banner():
    """Afficher bannière de démarrage"""
    print()
    print("=" * 70)
    print("  🏎️  MOTORSPORT DIGEST - WEEKLY GENERATION  🏎️")
    print("=" * 70)
    print()


def generate_weekly_digest(
    days_back=7,
    max_articles_extract=100,  # Augmenté : 50 → 100
    max_articles_summarize=20,  # Augmenté : 15 → 20
    min_relevance_score=20,
    language='fr'
):
    """
    Pipeline complet génération digest hebdomadaire
    
    Args:
        days_back: Nombre de jours à récupérer
        max_articles_extract: Nombre max d'articles à extraire en détail
        max_articles_summarize: Nombre max d'articles à résumer (IA)
        min_relevance_score: Score minimum pour garder article
        language: Langue des résumés ('fr' ou 'en')
    
    Returns:
        DataFrame avec résumés générés
    """
    
    print_banner()
    
    start_time = datetime.now()
    
    # ============================================
    # ÉTAPE 1 : FETCH RSS FEEDS
    # ============================================
    
    print("📡 ÉTAPE 1/6 : Récupération flux RSS")
    print("-" * 70)
    
    try:
        articles_df = fetch_rss_feeds()
        
        if articles_df.empty:
            print("❌ ERROR: No articles fetched!")
            print("   This might be a network/SSL issue in GitHub Actions")
            return pd.DataFrame()
        
    except Exception as e:
        print(f"❌ ERROR fetching RSS: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()
    
    # ============================================
    # ÉTAPE 2 : FILTER RECENT
    # ============================================
    
    print("🔍 ÉTAPE 2/6 : Filtrage articles récents")
    print("-" * 70)
    
    try:
        recent_df = filter_recent_articles(articles_df, hours=days_back*24)
        
        if recent_df.empty:
            print("⚠️  WARNING: No recent articles found!")
            print("   Tip: Increase days_back parameter")
            return pd.DataFrame()
        
    except Exception as e:
        print(f"❌ ERROR filtering: {e}")
        return pd.DataFrame()
    
    # ============================================
    # ÉTAPE 3 : EXTRACT FULL CONTENT
    # ============================================
    
    print("📄 ÉTAPE 3/6 : Extraction contenu complet")
    print("-" * 70)
    
    try:
        # Prendre URLs uniques
        urls_to_extract = recent_df['link'].drop_duplicates().tolist()
        
        # Limiter nombre d'extractions
        if len(urls_to_extract) > max_articles_extract:
            print(f"  ℹ️  Limiting extraction to {max_articles_extract} articles")
            urls_to_extract = urls_to_extract[:max_articles_extract]
        
        # Extraire
        full_articles = extract_batch_articles(urls_to_extract, delay=1)
        
        if not full_articles:
            print("⚠️  WARNING: Could not extract any articles!")
            print("   Falling back to RSS summaries only...")
            # Utiliser summary RSS comme fallback
            recent_df['text'] = recent_df['summary']
            merged_df = recent_df
        else:
            # Merger avec metadata RSS
            full_df = pd.DataFrame(full_articles)
            merged_df = recent_df.merge(
                full_df[['url', 'text']], 
                left_on='link', 
                right_on='url', 
                how='left'
            )
            
            # Remplir texte manquant avec summary RSS
            merged_df['text'] = merged_df['text'].fillna(merged_df['summary'])
        
    except Exception as e:
        print(f"❌ ERROR extracting: {e}")
        print("   Using RSS summaries as fallback...")
        recent_df['text'] = recent_df['summary']
        merged_df = recent_df
    
    # ============================================
    # ÉTAPE 4 : SCORE & RANK
    # ============================================
    
    print("🎯 ÉTAPE 4/6 : Scoring et classement")
    print("-" * 70)
    
    try:
        # Scorer tous les articles
        ranked_df = rank_articles(merged_df)
        
        # Filtrer par score minimum
        filtered_df = ranked_df[ranked_df['relevance_score'] >= min_relevance_score].copy()
        
        print(f"  ✅ Kept {len(filtered_df)} articles with score >= {min_relevance_score}")
        
        # DÉDUPLICATION (même news de sources différentes)
        filtered_df = deduplicate_articles(filtered_df, similarity_threshold=0.7)
        print()
        
        if filtered_df.empty:
            print("⚠️  WARNING: No articles passed relevance filter!")
            print("   Tip: Lower min_relevance_score")
            return pd.DataFrame()
        
        # Sauvegarder en base
        save_to_database(filtered_df)
        
    except Exception as e:
        print(f"❌ ERROR scoring: {e}")
        return pd.DataFrame()
    
    # ============================================
    # ÉTAPE 5 : AI SUMMARIZATION
    # ============================================
    
    print("🤖 ÉTAPE 5/6 : Génération résumés IA")
    print("-" * 70)
    
    try:
        # Estimer coût d'abord
        cost = estimate_cost(min(max_articles_summarize, len(filtered_df)))
        print(f"💰 Estimated cost: ${cost['total_cost']:.4f}\n")
        
        # Générer résumés BILINGUES (FR + EN)
        summaries_df = summarize_batch_bilingual(
            filtered_df,
            max_articles=max_articles_summarize,
            delay=1
        )
        
        if summaries_df.empty:
            print("❌ ERROR: No summaries generated!")
            return pd.DataFrame()
        
    except Exception as e:
        print(f"❌ ERROR summarizing: {e}")
        return pd.DataFrame()
    
    # ============================================
    # ÉTAPE 6 : GENERATE WEB PAGE
    # ============================================
    
    print("🌐 ÉTAPE 6/6 : Génération page web")
    print("-" * 70)
    
    try:
        # Préparer articles additionnels (21-40)
        additional_articles = None
        if len(filtered_df) > max_articles_summarize:
            additional_articles = filtered_df.iloc[max_articles_summarize:max_articles_summarize+20]
        
        # Générer HTML BILINGUE avec articles additionnels
        generate_bilingual_html(
            summaries_df, 
            additional_articles_df=additional_articles,
            output_path='docs/latest.html'
        )
        
    except Exception as e:
        print(f"❌ ERROR generating web page: {e}")
        return pd.DataFrame()
    
    # ============================================
    # SUMMARY
    # ============================================
    
    elapsed = datetime.now() - start_time
    
    print("=" * 70)
    print("✅ DIGEST GENERATION COMPLETE!")
    print("=" * 70)
    print()
    print(f"📊 Summary:")
    print(f"  • Total articles fetched: {len(articles_df)}")
    print(f"  • Recent articles: {len(recent_df)}")
    print(f"  • Articles extracted: {len(full_articles) if full_articles else 0}")
    print(f"  • Articles scored: {len(ranked_df)}")
    print(f"  • Articles filtered (score >= {min_relevance_score}): {len(filtered_df)}")
    print(f"  • Summaries generated: {len(summaries_df)}")
    print()
    print(f"⏱️  Time elapsed: {elapsed.total_seconds():.1f} seconds")
    print(f"💰 Estimated cost: ${cost['total_cost']:.4f}")
    print()
    print("🌐 Access your digest:")
    print(f"   • Local: file://{os.path.abspath('docs/latest.html')}")
    print(f"   • GitHub Pages: https://[username].github.io/motorsport-digest/")
    print()
    print("=" * 70)
    
    return summaries_df


# ============================================
# CLI INTERFACE
# ============================================

def main():
    """Point d'entrée principal"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate motorsport weekly digest',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python veille_motorsport/main.py                    # Default: 7 days, 15 summaries, FR
  python veille_motorsport/main.py --days 14          # Last 2 weeks
  python veille_motorsport/main.py --max-summaries 20 # 20 summaries
  python veille_motorsport/main.py --lang en          # English summaries
  python veille_motorsport/main.py --min-score 40     # Higher quality filter
        """
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back (default: 7)'
    )
    
    parser.add_argument(
        '--max-extract',
        type=int,
        default=100,  # Augmenté: 50 → 100
        help='Max articles to extract full content (default: 100)'
    )
    
    parser.add_argument(
        '--max-summaries',
        type=int,
        default=20,  # Augmenté: 15 → 20
        help='Max articles to summarize with AI (default: 20)'
    )
    
    parser.add_argument(
        '--min-score',
        type=int,
        default=20,
        help='Minimum relevance score to keep (default: 20)'
    )
    
    parser.add_argument(
        '--lang',
        choices=['fr', 'en'],
        default='fr',
        help='Language for summaries (default: fr)'
    )
    
    args = parser.parse_args()
    
    # Générer digest
    summaries = generate_weekly_digest(
        days_back=args.days,
        max_articles_extract=args.max_extract,
        max_articles_summarize=args.max_summaries,
        min_relevance_score=args.min_score,
        language=args.lang
    )
    
    # Exit code
    if summaries.empty:
        print("\n❌ Digest generation failed!")
        sys.exit(1)
    else:
        print("\n✅ Success!")
        sys.exit(0)


if __name__ == "__main__":
    main()
