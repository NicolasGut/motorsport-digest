"""
RSS Aggregator Module
Récupère et agrège les flux RSS des sources motorsport
"""

import feedparser
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# ============================================
# SOURCES RSS - Motorsport
# ============================================

RSS_FEEDS = {
    # F1 - Sources officielles
    'F1_Official': 'https://www.formula1.com/en/latest/all.xml',
    
    # WEC / Endurance
    'FIA_WEC': 'https://www.fiawec.com/en/rss',
    
    # Médias spécialisés majeurs
    'Autosport': 'https://www.autosport.com/rss/feed/all',
    'The_Race': 'https://www.the-race.com/feed/',
    'Motorsport_com': 'https://www.motorsport.com/rss/all/news/',
    'RaceFans': 'https://www.racefans.net/feed/',
    
    # Technique
    'F1_Technical': 'https://www.f1technical.net/rss',
    
    # Vous pouvez ajouter d'autres sources ici
    # 'Votre_Source': 'https://example.com/rss',
}


def fetch_rss_feeds(feeds_dict=None):
    """
    Récupérer tous les flux RSS
    
    Args:
        feeds_dict: Dictionnaire optionnel de feeds (utilise RSS_FEEDS par défaut)
    
    Returns:
        DataFrame avec tous les articles
    """
    
    if feeds_dict is None:
        feeds_dict = RSS_FEEDS
    
    articles = []
    
    print(f"📡 Fetching {len(feeds_dict)} RSS feeds...\n")
    
    for source_name, rss_url in feeds_dict.items():
        print(f"  → {source_name}...", end=" ")
        
        try:
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:  # Erreur de parsing
                print(f"⚠️  Warning: {feed.bozo_exception}")
                continue
            
            count = 0
            for entry in feed.entries:
                article = {
                    'source': source_name,
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', entry.get('updated', '')),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'fetched_at': datetime.now().isoformat()
                }
                articles.append(article)
                count += 1
            
            print(f"✅ {count} articles")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✅ Total: {len(articles)} articles fetched\n")
    
    return pd.DataFrame(articles)


def filter_recent_articles(df, hours=168):
    """
    Filtrer articles récents (par défaut 7 jours = 168h)
    """
    
    if df.empty:
        print("⚠️  No articles to filter")
        return df
    
    print(f"🔍 Filtering articles from last {hours} hours ({hours//24} days)...")
    
    # Parser dates (formats variés selon sources)
    df['published_dt'] = pd.to_datetime(df['published'], errors='coerce', utc=True)
    
    # Garder articles avec date valide
    df_with_date = df[df['published_dt'].notna()].copy()
    
    # Filtrer par date (avec timezone UTC)
    from datetime import timezone
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = df_with_date[df_with_date['published_dt'] >= cutoff].copy()
    
    # Trier par date (plus récent en premier)
    recent = recent.sort_values('published_dt', ascending=False)
    
    print(f"✅ {len(recent)} recent articles (from {len(df)} total)\n")
    
    return recent


def save_to_database(df, db_path='data/veille_motorsport.db'):
    """
    Sauvegarder articles dans SQLite (évite doublons)
    
    Args:
        df: DataFrame avec articles
        db_path: Chemin base de données
    """
    
    if df.empty:
        print("⚠️  No articles to save")
        return
    
    print(f"💾 Saving to database: {db_path}...")
    
    # Créer dossier data si nécessaire
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    try:
        # Sauvegarder (append)
        df.to_sql('articles', conn, if_exists='append', index=False)
        
        # Supprimer doublons (basé sur URL)
        conn.execute('''
            DELETE FROM articles
            WHERE rowid NOT IN (
                SELECT MIN(rowid)
                FROM articles
                GROUP BY link
            )
        ''')
        
        conn.commit()
        
        # Compter total articles en base
        cursor = conn.execute("SELECT COUNT(*) FROM articles")
        total = cursor.fetchone()[0]
        
        print(f"✅ Database updated: {total} unique articles total\n")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    finally:
        conn.close()


def get_articles_from_db(db_path='data/veille_motorsport.db', days=7):
    """
    Récupérer articles depuis la base de données
    
    Args:
        db_path: Chemin base de données
        days: Nombre de jours à récupérer
    
    Returns:
        DataFrame avec articles
    """
    
    if not os.path.exists(db_path):
        print(f"⚠️  Database not found: {db_path}")
        return pd.DataFrame()
    
    conn = sqlite3.connect(db_path)
    
    try:
        query = f"""
            SELECT * FROM articles
            WHERE published_dt >= datetime('now', '-{days} days')
            ORDER BY published_dt DESC
        """
        
        df = pd.read_sql_query(query, conn)
        print(f"📚 Loaded {len(df)} articles from database\n")
        
        return df
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return pd.DataFrame()
    
    finally:
        conn.close()


# ============================================
# TEST MODULE
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("RSS AGGREGATOR - TEST")
    print("=" * 60)
    print()
    
    # Test 1: Fetch feeds
    articles_df = fetch_rss_feeds()
    
    if not articles_df.empty:
        # Test 2: Filter recent
        recent_df = filter_recent_articles(articles_df, hours=168)  # 7 jours
        
        # Test 3: Save to database
        save_to_database(recent_df)
        
        # Test 4: Display sample
        print("📰 Sample articles:\n")
        for idx, row in recent_df.head(5).iterrows():
            print(f"{idx+1}. [{row['source']}] {row['title']}")
            print(f"   {row['link']}")
            print()
    else:
        print("❌ No articles fetched!")
    
    print("=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
