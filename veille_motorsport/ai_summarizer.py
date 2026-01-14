"""
AI Summarizer Module
Génère des résumés automatiques d'articles avec Claude API
"""

import anthropic
import os
import pandas as pd
from datetime import datetime
import time

# Charger variables d'environnement
from dotenv import load_dotenv
load_dotenv()


def summarize_article_claude(article_text, article_title, article_url, language='fr'):
    """
    Résumer un article avec Claude API
    
    Args:
        article_text: Texte complet article
        article_title: Titre article
        article_url: URL article
        language: Langue résumé ('fr' ou 'en')
    
    Returns:
        Résumé texte ou None si erreur
    """
    
    # Vérifier API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment!")
        print("   Please add it to your .env file")
        return None
    
    # Tronquer texte si trop long (économiser tokens)
    max_text_length = 4000
    if len(article_text) > max_text_length:
        article_text = article_text[:max_text_length] + "..."
    
    # Préparer prompt selon langue
    if language == 'fr':
        prompt = f"""Résume cet article motorsport en français.

Titre : {article_title}
URL : {article_url}

Article :
{article_text}

Instructions :
- 2-3 phrases concises et informatives
- Focus sur l'information technique ou sportive clé
- Ton professionnel et factuel (style journaliste data)
- 100-150 mots maximum
- Pas de sensationnalisme
- Si l'article parle de data/stratégie/technique, mettre l'accent dessus

Résumé :"""
    else:  # english
        prompt = f"""Summarize this motorsport article in English.

Title: {article_title}
URL: {article_url}

Article:
{article_text}

Instructions:
- 2-3 concise and informative sentences
- Focus on key technical or sporting information
- Professional and factual tone (data journalist style)
- 100-150 words maximum
- No sensationalism
- If the article discusses data/strategy/technical aspects, emphasize them

Summary:"""
    
    try:
        # Créer client Claude - version simple sans proxies
        client = anthropic.Anthropic(
            api_key=api_key,
            max_retries=2,
            timeout=30.0
        )
        
        # Appel API
        message = client.messages.create(
            model="claude-sonnet-4-20250514",  # Dernière version Sonnet
            max_tokens=300,
            temperature=0.7,  # Un peu de créativité mais restant factuel
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extraire résumé
        summary = message.content[0].text.strip()
        
        return summary
        
    except anthropic.AuthenticationError:
        print("❌ Authentication error: Invalid API key")
        return None
    
    except anthropic.APIError as e:
        print(f"❌ API error: {e}")
        return None
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def summarize_batch(articles_df, max_articles=15, delay=1, language='fr'):
    """
    Résumer batch d'articles (top articles seulement)
    
    Args:
        articles_df: DataFrame avec articles
        max_articles: Nombre max d'articles à résumer
        delay: Délai entre appels API (secondes)
        language: Langue résumés
    
    Returns:
        DataFrame avec résumés
    """
    
    if articles_df.empty:
        print("⚠️  No articles to summarize")
        return pd.DataFrame()
    
    # Prendre top articles (par score si disponible)
    if 'relevance_score' in articles_df.columns:
        top_articles = articles_df.nlargest(max_articles, 'relevance_score')
    else:
        top_articles = articles_df.head(max_articles)
    
    summaries = []
    total = len(top_articles)
    
    print(f"🤖 Generating AI summaries for {total} articles...\n")
    
    for idx, row in top_articles.iterrows():
        print(f"  [{len(summaries)+1}/{total}] Summarizing...", end=" ")
        
        try:
            summary = summarize_article_claude(
                row.get('text', row.get('summary', '')),
                row['title'],
                row['link'],
                language=language
            )
            
            if summary:
                summaries.append({
                    'url': row['link'],
                    'title': row['title'],
                    'summary': summary,
                    'score': row.get('relevance_score', 0),
                    'source': row.get('source', ''),
                    'published': row.get('published', ''),
                    'summarized_at': datetime.now().isoformat()
                })
                
                print(f"✅ ({len(summary)} chars)")
            else:
                print("❌ Failed")
            
            # Rate limiting (respecter API limits)
            if len(summaries) < total:
                time.sleep(delay)
                
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            break
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✅ Successfully summarized {len(summaries)}/{total} articles\n")
    
    # Calculer coût approximatif
    avg_tokens_per_summary = 200  # Estimation
    total_tokens = len(summaries) * avg_tokens_per_summary
    cost_estimate = (total_tokens / 1_000_000) * 15  # $15 per MTok output
    
    print(f"💰 Estimated cost: ${cost_estimate:.4f}\n")
    
    return pd.DataFrame(summaries)


def estimate_cost(num_articles, avg_article_length=2000):
    """
    Estimer coût API pour batch d'articles
    
    Args:
        num_articles: Nombre d'articles
        avg_article_length: Longueur moyenne (caractères)
    
    Returns:
        Dict avec estimation coûts
    """
    
    # Estimation tokens (1 token ≈ 4 chars)
    input_tokens_per_article = avg_article_length / 4
    output_tokens_per_article = 150 / 4  # ~150 mots résumé
    
    total_input_tokens = num_articles * input_tokens_per_article
    total_output_tokens = num_articles * output_tokens_per_article
    
    # Prix Claude Sonnet (Jan 2025)
    cost_input = (total_input_tokens / 1_000_000) * 3   # $3/MTok input
    cost_output = (total_output_tokens / 1_000_000) * 15  # $15/MTok output
    
    total_cost = cost_input + cost_output
    
    return {
        'num_articles': num_articles,
        'input_tokens': int(total_input_tokens),
        'output_tokens': int(total_output_tokens),
        'cost_input': cost_input,
        'cost_output': cost_output,
        'total_cost': total_cost
    }


# ============================================
# TEST MODULE
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("AI SUMMARIZER - TEST")
    print("=" * 60)
    print()
    
    # Vérifier API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not set!")
        print()
        print("Please create a .env file with:")
        print("  ANTHROPIC_API_KEY=your_api_key_here")
        print()
        print("Get your key at: https://console.anthropic.com/")
        exit(1)
    
    print("✅ API key found\n")
    
    # Article de test
    test_article = {
        'title': 'F1 Data Analytics Revolution: How Teams Use Machine Learning',
        'text': '''Formula 1 teams are increasingly relying on advanced data analytics 
        and machine learning to gain competitive advantages. Telemetry data from hundreds 
        of sensors is analyzed in real-time to optimize race strategies, predict tire 
        degradation, and improve car performance. Mercedes and Red Bull have invested 
        heavily in data science teams, using predictive models to simulate race scenarios 
        and make split-second decisions during races.''',
        'link': 'https://example.com/test-article',
        'source': 'F1_Technical',
        'relevance_score': 85
    }
    
    print("Testing summarization on sample article:\n")
    print(f"Title: {test_article['title']}")
    print(f"Text length: {len(test_article['text'])} chars\n")
    
    # Test résumé FR
    print("Generating French summary...\n")
    summary_fr = summarize_article_claude(
        test_article['text'],
        test_article['title'],
        test_article['link'],
        language='fr'
    )
    
    if summary_fr:
        print("✅ Summary (FR):")
        print(f"  {summary_fr}\n")
    
    # Test résumé EN
    print("Generating English summary...\n")
    summary_en = summarize_article_claude(
        test_article['text'],
        test_article['title'],
        test_article['link'],
        language='en'
    )
    
    if summary_en:
        print("✅ Summary (EN):")
        print(f"  {summary_en}\n")
    
    # Test estimation coût
    print("=" * 60)
    print("\nCost estimation for 15 articles/week:")
    
    cost = estimate_cost(15)
    print(f"  • Input tokens: {cost['input_tokens']:,}")
    print(f"  • Output tokens: {cost['output_tokens']:,}")
    print(f"  • Cost input: ${cost['cost_input']:.4f}")
    print(f"  • Cost output: ${cost['cost_output']:.4f}")
    print(f"  • Total cost: ${cost['total_cost']:.4f}")
    print(f"  • Monthly (4 weeks): ${cost['total_cost']*4:.2f}")
    print(f"  • Yearly (52 weeks): ${cost['total_cost']*52:.2f}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
