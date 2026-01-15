"""
Article Deduplicator Module
Détecte et élimine les doublons d'articles (même news de sources différentes)
"""

from difflib import SequenceMatcher
import pandas as pd


def calculate_similarity(str1, str2):
    """
    Calculer similarité entre 2 strings (0 à 1)
    Amélioration : détection de mots-clés communs pour doublons
    
    Args:
        str1, str2: Strings à comparer
    
    Returns:
        Score similarité (0 = différent, 1 = identique)
    """
    from difflib import SequenceMatcher
    
    # Similarité de base
    base_similarity = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    # AMÉLIORATION : Extraction mots-clés importants (noms propres, nombres)
    # Patterns : BMW, Ferrari, Rossi, Newey, F1, 2026, etc.
    import re
    
    # Mots importants (2+ caractères, commence par majuscule ou nombre)
    pattern = r'\b(?:[A-Z][a-z]+|[A-Z]{2,}|\d+)\b'
    
    words1 = set(re.findall(pattern, str1))
    words2 = set(re.findall(pattern, str2))
    
    if words1 and words2:
        # Jaccard similarity sur mots-clés
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        keyword_similarity = intersection / union if union > 0 else 0
        
        # Pondération : 60% base + 40% mots-clés
        final_similarity = (base_similarity * 0.6) + (keyword_similarity * 0.4)
        
        return final_similarity
    
    return base_similarity


def deduplicate_articles(df, similarity_threshold=0.7):
    """
    Éliminer articles en double (même news de sources différentes)
    
    Stratégie :
    - Compare titres par paires
    - Si similarité > threshold → garde article avec meilleur score
    - Si scores égaux → garde source la plus fiable
    
    Args:
        df: DataFrame avec colonnes 'title', 'score', 'source'
        similarity_threshold: Seuil similarité (0.7 = 70% similaire)
    
    Returns:
        DataFrame sans doublons
    """
    
    if df.empty or len(df) < 2:
        return df
    
    print(f"🔍 Checking for duplicates (threshold: {similarity_threshold})...")
    
    # Hiérarchie sources (plus fiable = plus haut)
    SOURCE_PRIORITY = {
        # Officiels (priorité max)
        'f1_official': 10,
        'formulae_official': 10,
        'fia': 10,
        
        # Techniques spécialisés
        'f1_technical': 9,
        'racecar': 9,
        'sportscar365': 9,
        
        # Médias majeurs techniques
        'autosport': 8,
        'motorsport': 8,
        'the_race': 8,
        'racefans': 7,
        
        # Autres
        'default': 5
    }
    
    def get_source_priority(source):
        """Obtenir priorité d'une source"""
        source_lower = source.lower()
        for key, priority in SOURCE_PRIORITY.items():
            if key in source_lower:
                return priority
        return SOURCE_PRIORITY['default']
    
    # Marquer articles à garder
    keep_indices = []
    skip_indices = set()
    
    # Utiliser 'relevance_score' si disponible, sinon 'score'
    score_col = 'relevance_score' if 'relevance_score' in df.columns else 'score'
    df_sorted = df.sort_values(score_col, ascending=False).reset_index(drop=True)
    
    duplicates_found = 0
    
    for i in range(len(df_sorted)):
        if i in skip_indices:
            continue
        
        keep_indices.append(i)
        title_i = df_sorted.loc[i, 'title']
        score_i = df_sorted.loc[i, score_col]
        source_i = df_sorted.loc[i, 'source']
        
        # Comparer avec articles suivants
        for j in range(i + 1, len(df_sorted)):
            if j in skip_indices:
                continue
            
            title_j = df_sorted.loc[j, 'title']
            similarity = calculate_similarity(title_i, title_j)
            
            if similarity >= similarity_threshold:
                # Doublon détecté !
                score_j = df_sorted.loc[j, score_col]
                source_j = df_sorted.loc[j, 'source']
                
                # Décider lequel garder
                if score_i > score_j:
                    # Garder i, skip j
                    skip_indices.add(j)
                    duplicates_found += 1
                    print(f"  → Duplicate: '{title_j[:60]}...' (score {score_j}) - keeping better scored version")
                
                elif score_i < score_j:
                    # Garder j, skip i
                    keep_indices.remove(i)
                    skip_indices.add(i)
                    duplicates_found += 1
                    print(f"  → Duplicate: '{title_i[:60]}...' (score {score_i}) - keeping better scored version")
                    break  # i est skipped, passer au suivant
                
                else:
                    # Scores égaux → comparer sources
                    priority_i = get_source_priority(source_i)
                    priority_j = get_source_priority(source_j)
                    
                    if priority_i >= priority_j:
                        skip_indices.add(j)
                        duplicates_found += 1
                        print(f"  → Duplicate: '{title_j[:60]}...' - keeping from {source_i}")
                    else:
                        keep_indices.remove(i)
                        skip_indices.add(i)
                        duplicates_found += 1
                        print(f"  → Duplicate: '{title_i[:60]}...' - keeping from {source_j}")
                        break
    
    # Créer DataFrame sans doublons
    df_deduped = df_sorted.loc[keep_indices].copy()
    
    print(f"✅ Removed {duplicates_found} duplicates ({len(df)} → {len(df_deduped)} articles)\n")
    
    return df_deduped


# ============================================
# TEST MODULE
# ============================================

if __name__ == "__main__":
    
    print("=" * 70)
    print("DEDUPLICATOR - TEST")
    print("=" * 70)
    
    # Test data
    test_articles = pd.DataFrame({
        'title': [
            'McLaren signs Jensen for WEC 2027 Hypercar programme',
            'McLaren Names Jensen as First Hypercar Driver for 2027 Debut',
            'McLaren announces first driver for 2027 WEC Hypercar programme',
            'Cadillac launches stealthy first F1 livery for Barcelona testing',
            'Cadillac reveal Barcelona shakedown livery for new team first F1 test',
            'Different article about something else entirely',
        ],
        'score': [85, 82, 80, 75, 73, 90],
        'source': ['Autosport', 'Motorsport', 'The_Race', 'F1_Official', 'RaceFans', 'F1_Technical']
    })
    
    print("\n📰 Original articles:")
    for idx, row in test_articles.iterrows():
        print(f"{idx+1}. [{row['source']}] {row['title']} (score: {row['score']})")
    
    print(f"\nTotal: {len(test_articles)} articles\n")
    
    # Deduplicate
    deduped = deduplicate_articles(test_articles, similarity_threshold=0.7)
    
    print("\n📰 After deduplication:")
    for idx, row in deduped.iterrows():
        print(f"{idx+1}. [{row['source']}] {row['title']} (score: {row['score']})")
    
    print(f"\nTotal: {len(deduped)} articles")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
