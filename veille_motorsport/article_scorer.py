"""
Article Scorer v2 - Système de scoring simplifié et efficace
Principe : FILTRAGE puis SCORING
"""

# ============================================
# ÉTAPE 1 : FILTRAGE - Sports acceptés/rejetés
# ============================================

# Sports ACCEPTÉS (périmètre du digest)
SPORTS_ACCEPTED = [
    # F1 et formules monoplace
    'formula 1', 'f1', 'formula one',
    'formula 2', 'f2',
    'formula 3', 'f3',
    'super formula',
    'f1 academy',
    
    # Endurance et GT
    'wec', 'world endurance', 'le mans', 'lmp', 'hypercar',
    'gt world challenge', 'gtwc', 'gt3', 'gt4',
    'imsa', 'gtd', 'gtp',
    'spa 24', 'nurburgring 24', 'bathurst 12', 'daytona 24', 'rolex 24',
    
    # Formule E (uniquement le terme complet pour éviter faux positifs)
    'formula e',  # Supprimé 'fe' car trop de faux positifs
]

# Sports REJETÉS (hors périmètre)
SPORTS_REJECTED = [
    # Rally et cross
    'wrc', 'world rally', 'rallying', 'rally championship',
    'dakar', 'rally raid',
    'rallycross',
    
    # Moto
    'motogp', 'moto2', 'moto3',
    'superbike', 'sbk',
    'vr46', 'rossi bike', 'rossi team', "rossi's vr46",
    
    # IndyCar et ovales US
    'indycar', 'indy nxt', 'indy 500', 'indianapolis 500',
    'indy lights',
    
    # NASCAR et US
    'nascar', 'cup series', 'xfinity',
    'chili bowl',
    
    # Karting (sauf si pilote F1/WEC mentionné dans titre)
    'karting academy', 'karting championship', 'karting series',
    'opens registrations for', 'karting returns',
    
    # Autres
    'drag racing',
    'drifting', 'drift championship',
    'formula student',
]

# Mots-clés GOSSIP à rejeter (ventes, lifestyle)
GOSSIP_REJECTED = [
    # Ventes aux enchères
    'heads to auction', 'auction with', 'expected to fetch',
    'auction estimate',
    
    # Collectibles et jouets
    'meccano', 'lego', 'scale model', '1:8-scale', '1:18-scale',
    'trading card', 'memorabilia',
    
    # Lifestyle gossip
    'spotted driving', 'seen driving', 'rare car',
    'girlfriend', 'boyfriend', 'dating', 'relationship',
    'vacation', 'holiday',
    
    # Fan gossip & social media drama
    'fans lose it', 'fans deliver verdict', 'fans erupt',
    'twitter rant', 'social media rant', 'social media erupts',
    'describes rivals as', 'calls out', 'slams',
    
    # Faits divers
    'stolen kart', 'kart recovered', 'theft',
    'round-up:', 'news round-up',
]

# ============================================
# ÉTAPE 2 : SCORING - Qualité du contenu
# ============================================

# NIVEAU 1 - TECHNIQUE & PERFORMANCE (score max : +60)
KEYWORDS_TECHNICAL = {
    # Data & IA (poids max)
    'artificial intelligence': 15,
    'machine learning': 15,
    'data analytics': 12,
    'algorithm': 12,
    'telemetry': 10,
    'simulation': 10,
    'predictive': 10,
    
    # Technique pure
    'aerodynamics': 10,
    'aero': 8,
    'downforce': 10,
    'drag': 8,
    'ground effect': 10,
    'suspension': 8,
    'power unit': 10,
    'hybrid': 8,
    'ers': 10,
    'drs': 8,
    'tire compound': 10,
    'tire strategy': 8,
    'cooling': 8,
    'reliability': 8,
    'lap time': 8,
    'pace': 6,
    'performance': 6,
    'development': 6,
    'testing': 6,
}

# NIVEAU 2 - BUSINESS & ÉCURIES (score max : +40)
KEYWORDS_BUSINESS = {
    # Partenariats et business
    'partnership': 10,
    'sponsor': 8,
    'technical partnership': 12,
    'deal': 8,
    'contract': 6,
    'investment': 10,
    'funding': 10,
    'acquisition': 10,
    
    # Management et stratégie
    'team principal': 8,
    'technical director': 8,
    'ceo': 8,
    'strategy': 8,
    'recruitment': 6,
    'hiring': 6,
    
    # Règlements et innovation
    'regulation': 8,
    'technical directive': 10,
    'efuel': 10,
    'e-fuel': 10,
    'sustainability': 8,
    'carbon neutral': 8,
}

# NIVEAU 3 - ACTUALITÉS GÉNÉRALES (score max : +20)
KEYWORDS_GENERAL = {
    # Design et branding
    'livery': 6,
    'design': 5,
    'branding': 5,
    
    # Pilotes et transferts
    'driver': 4,
    'signs': 5,
    'announces': 5,
    'confirms': 5,
    
    # Course
    'race': 3,
    'championship': 4,
    'podium': 3,
    'victory': 3,
}

# ÉCURIES - Liste complète pour détection
TEAMS_F1 = [
    'mercedes', 'ferrari', 'red bull', 'mclaren', 'alpine',
    'aston martin', 'williams', 'haas', 'sauber', 'stake',
    'racing bulls', 'rb', 'visa rb', 'cadillac',
]

TEAMS_WEC_GT = [
    'toyota', 'ferrari', 'porsche', 'cadillac', 'bmw',
    'peugeot', 'alpine', 'lamborghini', 'aston martin',
    'corvette', 'ford',
]

# CONSTRUCTEURS - Tous les constructeurs majeurs
CONSTRUCTEURS = [
    'mercedes', 'ferrari', 'red bull', 'honda', 'renault',
    'toyota', 'porsche', 'bmw', 'audi', 'lamborghini',
    'mclaren', 'aston martin', 'ford', 'chevrolet', 'cadillac',
]

# PILOTES MAJEURS - Top pilotes à suivre
PILOTES_MAJEURS = [
    # F1 actuels
    'verstappen', 'hamilton', 'leclerc', 'norris', 'sainz',
    'russell', 'alonso', 'piastri', 'perez', 'gasly',
    
    # F1 légendes/experts
    'newey', 'adrian newey', 'horner', 'wolff', 'binotto',
    'vasseur',
    
    # WEC/Endurance
    'kobayashi', 'buemi', 'hartley', 'conway',
    'pier guidi', 'calado', 'molina',
]


# ============================================
# FONCTION DE SCORING
# ============================================

def score_article_v2(article_text, article_title, source=''):
    """
    Scorer un article selon le nouveau système simplifié
    
    Logique :
    1. FILTRAGE : Sport accepté ? Gossip ? → Rejet immédiat (score 0)
    2. SCORING : Qualité contenu (technique > business > général)
    
    Args:
        article_text: Contenu article
        article_title: Titre
        source: Source (optionnel)
    
    Returns:
        Score 0-100
    """
    
    # Combiner titre + texte (titre compte 2x)
    text_full = f"{article_title} {article_title} {article_text}".lower()
    title_lower = article_title.lower()
    
    # ============================================
    # ÉTAPE 1 : FILTRAGE BINAIRE
    # ============================================
    
    # 1A. Vérifier sports REJETÉS → Score 0 immédiat
    for sport_rejected in SPORTS_REJECTED:
        if sport_rejected in text_full:
            # Exception : Si article mentionne aussi sport accepté ET contexte technique
            has_accepted_sport = any(sport in text_full for sport in SPORTS_ACCEPTED)
            has_technical = any(kw in text_full for kw in ['partnership', 'technical', 'development'])
            
            if not (has_accepted_sport and has_technical):
                return 0  # REJET
    
    # 1B. Vérifier GOSSIP rejeté → Score 0 immédiat
    for gossip in GOSSIP_REJECTED:
        if gossip in text_full:
            return 0  # REJET
    
    # 1C. Vérifier au moins UN sport accepté présent
    has_relevant_sport = any(sport in text_full for sport in SPORTS_ACCEPTED)
    if not has_relevant_sport:
        # Pas de sport explicite mais peut-être écurie F1/WEC ?
        has_team = any(team in text_full for team in TEAMS_F1 + TEAMS_WEC_GT)
        if not has_team:
            return 0  # REJET (aucun sport pertinent détecté)
    
    # ============================================
    # ÉTAPE 2 : SCORING QUALITÉ
    # ============================================
    
    score = 0
    
    # NIVEAU 1 : Technique & Performance (max 60 pts)
    for keyword, points in KEYWORDS_TECHNICAL.items():
        if keyword in text_full:
            score += points
    
    # Cap niveau 1
    score = min(score, 60)
    
    # NIVEAU 2 : Business & Écuries (max +40 pts)
    business_score = 0
    for keyword, points in KEYWORDS_BUSINESS.items():
        if keyword in text_full:
            business_score += points
    
    business_score = min(business_score, 40)
    score += business_score
    
    # NIVEAU 3 : Actualités générales (max +20 pts)
    general_score = 0
    for keyword, points in KEYWORDS_GENERAL.items():
        if keyword in text_full:
            general_score += points
    
    general_score = min(general_score, 20)
    score += general_score
    
    # BONUS : Pilotes/constructeurs majeurs (+5 pts)
    if any(pilote in text_full for pilote in PILOTES_MAJEURS):
        score += 5
    
    if any(constructeur in text_full for constructeur in CONSTRUCTEURS):
        score += 3
    
    # BONUS : Titre contient sport accepté (+10 pts)
    if any(sport in title_lower for sport in SPORTS_ACCEPTED):
        score += 10
    
    # BONUS : WEC/Endurance/GT explicite (+30 pts car moins couvert que F1)
    endurance_keywords = ['wec', 'le mans', 'hypercar', 'lmp', 'imsa', 'gt3', 'gt4', 'gtwc']
    if any(kw in text_full for kw in endurance_keywords):
        score += 30
    
    # BONUS : Article long = plus de substance (+5 pts)
    if len(article_text) > 1500:
        score += 5
    
    # Cap final
    score = min(score, 100)
    
    return score


# ============================================
# FONCTION DE RANKING (compatible avec ancien code)
# ============================================

def rank_articles(articles_df):
    """
    Classer articles avec nouveau scorer v2
    Compatible avec l'ancien pipeline
    """
    
    if articles_df.empty:
        print("⚠️  No articles to rank")
        return articles_df
    
    print("🎯 Scoring article relevance (v2 - simplified)...\n")
    
    # Calculer scores
    articles_df['relevance_score'] = articles_df.apply(
        lambda row: score_article_v2(
            row.get('text', ''),
            row.get('title', ''),
            row.get('source', '')
        ),
        axis=1
    )
    
    # Trier
    ranked = articles_df.sort_values('relevance_score', ascending=False)
    
    # Stats
    print(f"📊 Scoring statistics (v2):")
    print(f"  • Mean score: {ranked['relevance_score'].mean():.1f}")
    print(f"  • Median score: {ranked['relevance_score'].median():.1f}")
    print(f"  • Max score: {ranked['relevance_score'].max():.0f}")
    print(f"  • Articles > 50: {(ranked['relevance_score'] > 50).sum()}")
    print(f"  • Articles > 30: {(ranked['relevance_score'] > 30).sum()}")
    print(f"  • Articles REJECTED (score 0): {(ranked['relevance_score'] == 0).sum()}\n")
    
    return ranked


def get_top_articles(articles_df, n=20):
    """
    Obtenir top N articles (compatible ancien code)
    """
    if 'relevance_score' not in articles_df.columns:
        articles_df = rank_articles(articles_df)
    
    return articles_df.head(n)
