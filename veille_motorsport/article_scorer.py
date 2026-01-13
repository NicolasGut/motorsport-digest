"""
Article Scorer Module
Score la pertinence des articles selon des mots-clés techniques et thématiques
"""

import pandas as pd
import re

# ============================================
# KEYWORDS - Priorités différentes
# ============================================

# Mots-clés HAUTE priorité (data/technique)
KEYWORDS_HIGH_PRIORITY = [
    # Data & Analytics
    'data', 'analysis', 'analytics', 'telemetry', 'statistics', 'stats',
    'données', 'analyse', 'analytique', 'télémétrie', 'statistiques',
    
    # Machine Learning & AI
    'machine learning', 'ml', 'ai', 'artificial intelligence',
    'intelligence artificielle', 'algorithme', 'algorithm',
    'prediction', 'prédiction', 'model', 'modèle',
    
    # Technique & Performance
    'technical', 'technique', 'engineering', 'ingénierie',
    'performance', 'simulation', 'development', 'développement',
    'aérodynamique', 'aerodynamic', 'downforce', 'appui',
    
    # Stratégie
    'strategy', 'stratégie', 'pit stop', 'tire', 'pneu',
    'fuel', 'carburant', 'undercut', 'overcut',
]

# Mots-clés MOYENNE priorité (sport/général)
KEYWORDS_MEDIUM_PRIORITY = [
    # Course & Résultats
    'race', 'course', 'championship', 'championnat',
    'qualifying', 'qualifications', 'quali', 'grid',
    'podium', 'victory', 'victoire', 'win', 'winner',
    
    # Équipes & Pilotes
    'driver', 'pilote', 'team', 'écurie', 'équipe',
    'mercedes', 'ferrari', 'red bull', 'mclaren', 'alpine',
    'toyota', 'porsche', 'cadillac', 'bmw',
    
    # Règlements & Changements
    'regulation', 'règlement', 'rule', 'règle',
    'technical directive', 'directive technique',
    'fia', 'steward', 'penalty', 'pénalité',
]

# Mots-clés BASSE priorité (buzz/rumeurs)
KEYWORDS_LOW_PRIORITY = [
    'rumor', 'rumour', 'rumeur', 'gossip',
    'social media', 'twitter', 'instagram',
    'celebrity', 'célébrité', 'girlfriend', 'boyfriend',
]

# Mots-clés NÉGATIFS (à éviter)
KEYWORDS_NEGATIVE = [
    'clickbait', 'shocking', 'you won\'t believe',
    'scandal', 'drama', 'controversy',
    # Ajouter autres selon vos préférences
]


def score_article_relevance(article_text, article_title, source=''):
    """
    Scorer pertinence d'un article (0-100)
    
    Args:
        article_text: Texte complet article
        article_title: Titre article
        source: Source (optionnel, pour ajustement)
    
    Returns:
        Score de 0 à 100
    """
    
    if not article_text and not article_title:
        return 0
    
    # Combiner titre et texte (titre pèse plus)
    text_lower = f"{article_title} {article_title} {article_text}".lower()
    title_lower = article_title.lower()
    
    score = 0
    
    # === SCORING POSITIF ===
    
    # 1. Mots-clés HAUTE priorité (+10 pts chacun, max 50)
    high_matches = 0
    for keyword in KEYWORDS_HIGH_PRIORITY:
        if keyword.lower() in text_lower:
            high_matches += 1
            score += 10
    
    # Bonus si plusieurs mots-clés haute priorité
    if high_matches >= 3:
        score += 20
    
    # 2. Mots-clés MOYENNE priorité (+5 pts chacun, max 25)
    medium_matches = 0
    for keyword in KEYWORDS_MEDIUM_PRIORITY:
        if keyword.lower() in text_lower:
            medium_matches += 1
            score += 5
    
    # 3. BONUS si titre contient mots-clés importants (+20 pts)
    for keyword in KEYWORDS_HIGH_PRIORITY:
        if keyword.lower() in title_lower:
            score += 20
            break  # Une seule fois
    
    # 4. BONUS source officielle/technique
    technical_sources = ['f1_technical', 'racecar', 'fia', 'official']
    if any(src in source.lower() for src in technical_sources):
        score += 15
    
    # 5. BONUS longueur (articles longs souvent plus techniques)
    if len(article_text) > 2000:
        score += 10
    elif len(article_text) > 1000:
        score += 5
    
    # === SCORING NÉGATIF ===
    
    # 1. Mots-clés BASSE priorité (-5 pts chacun)
    for keyword in KEYWORDS_LOW_PRIORITY:
        if keyword.lower() in text_lower:
            score -= 5
    
    # 2. Mots-clés NÉGATIFS (clickbait, etc.) (-20 pts)
    for keyword in KEYWORDS_NEGATIVE:
        if keyword.lower() in text_lower:
            score -= 20
    
    # 3. Titre trop court ou trop long (-10 pts)
    title_len = len(article_title.split())
    if title_len < 4 or title_len > 20:
        score -= 10
    
    # === NORMALISATION ===
    
    # Cap entre 0 et 100
    score = max(0, min(100, score))
    
    return score


def rank_articles(articles_df):
    """
    Classer tous les articles par pertinence
    
    Args:
        articles_df: DataFrame avec colonnes 'text', 'title', 'source'
    
    Returns:
        DataFrame avec colonne 'relevance_score' ajoutée, trié
    """
    
    if articles_df.empty:
        print("⚠️  No articles to rank")
        return articles_df
    
    print("🎯 Scoring article relevance...\n")
    
    # Calculer score pour chaque article
    articles_df['relevance_score'] = articles_df.apply(
        lambda row: score_article_relevance(
            row.get('text', ''),
            row.get('title', ''),
            row.get('source', '')
        ),
        axis=1
    )
    
    # Trier par score (descending)
    ranked = articles_df.sort_values('relevance_score', ascending=False)
    
    # Stats
    print(f"📊 Scoring statistics:")
    print(f"  • Mean score: {ranked['relevance_score'].mean():.1f}")
    print(f"  • Median score: {ranked['relevance_score'].median():.1f}")
    print(f"  • Max score: {ranked['relevance_score'].max():.0f}")
    print(f"  • Articles > 50: {(ranked['relevance_score'] > 50).sum()}")
    print(f"  • Articles > 30: {(ranked['relevance_score'] > 30).sum()}\n")
    
    return ranked


def filter_by_score(articles_df, min_score=20):
    """
    Filtrer articles par score minimum
    
    Args:
        articles_df: DataFrame avec 'relevance_score'
        min_score: Score minimum pour garder
    
    Returns:
        DataFrame filtré
    """
    
    if 'relevance_score' not in articles_df.columns:
        print("⚠️  No relevance_score column, ranking first...")
        articles_df = rank_articles(articles_df)
    
    filtered = articles_df[articles_df['relevance_score'] >= min_score].copy()
    
    print(f"🔍 Filtered articles with score >= {min_score}")
    print(f"  • Kept: {len(filtered)}/{len(articles_df)} articles\n")
    
    return filtered


def get_top_articles(articles_df, n=15):
    """
    Récupérer les N meilleurs articles
    
    Args:
        articles_df: DataFrame avec 'relevance_score'
        n: Nombre d'articles à retourner
    
    Returns:
        DataFrame avec top N articles
    """
    
    if 'relevance_score' not in articles_df.columns:
        articles_df = rank_articles(articles_df)
    
    top = articles_df.nlargest(n, 'relevance_score')
    
    print(f"🏆 Top {n} articles selected\n")
    
    return top


# ============================================
# TEST MODULE
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("ARTICLE SCORER - TEST")
    print("=" * 60)
    print()
    
    # Articles de test
    test_articles = [
        {
            'title': 'F1 telemetry data analysis shows Ferrari strategy error',
            'text': 'Detailed analysis of telemetry data from the race reveals that Ferrari made a strategic error with their pit stop timing. Machine learning models predicted the optimal window...',
            'source': 'F1_Technical'
        },
        {
            'title': 'Hamilton wins dramatic race',
            'text': 'Lewis Hamilton won today in a dramatic finish. The crowd was excited.',
            'source': 'Motorsport_com'
        },
        {
            'title': 'You won\'t believe what this driver said!',
            'text': 'Shocking comments from driver about team. Social media is going crazy!',
            'source': 'Clickbait_News'
        },
    ]
    
    df_test = pd.DataFrame(test_articles)
    
    # Test scoring
    print("Testing relevance scoring:\n")
    
    for idx, row in df_test.iterrows():
        score = score_article_relevance(row['text'], row['title'], row['source'])
        print(f"{idx+1}. [{score:3.0f}] {row['title']}")
    
    print("\n" + "=" * 60)
    
    # Test ranking
    ranked = rank_articles(df_test)
    
    print("\nRanked articles:")
    for idx, row in ranked.iterrows():
        print(f"  [{row['relevance_score']:3.0f}] {row['title']}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
