"""
RSS Aggregator Module
Récupère et agrège les flux RSS des sources motorsport
"""

import feedparser
import pandas as pd
from datetime import datetime, timedelta, timezone
import sqlite3
import os

# ============================================
# FIX SSL pour macOS (développement local)
# ============================================
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# ============================================
# SOURCES RSS - Motorsport
# ============================================

RSS_FEEDS = {
    # ============================================
    # F1 - Sources officielles et majeures
    # ============================================
    'F1_Official': 'https://www.formula1.com/en/latest/all.xml',
    'Autosport': 'https://www.autosport.com/rss/feed/all',
    'The_Race': 'https://www.the-race.com/feed/',
    'Motorsport_com': 'https://www.motorsport.com/rss/all/news/',
    'RaceFans': 'https://www.racefans.net/feed/',
    
    # ============================================
    # F1 - Sources complémentaires
    # ============================================
    'PlanetF1': 'https://www.planetf1.com/feed/',
    'GPBlog': 'https://www.gpblog.com/en/rss/news.xml',
    'Crash_F1': 'https://www.crash.net/rss/f1',
    
    # ============================================
    # WEC / ENDURANCE - Sources RSS (Alternative)
    # ============================================
    'Autosport_WEC': 'https://www.autosport.com/wec/rss',
    'Motorsport_WEC': 'https://www.motorsport.com/wec/rss/news/',
    
    # ============================================
    # Note: FIA_WEC officiel sera scrapé via web_scraper.py
    # F1_Technical sera scrapé via web_scraper.py
    # ============================================
}


def fetch_rss_feeds(feeds_dict=None, include_scraped=True):
    """
    Récupérer tous les flux RSS + sources scrapées
    
    Args:
        feeds_dict: Dictionnaire optionnel de feeds (utilise RSS_FEEDS par défaut)
        include_scraped: Inclure sources scrapées (WEC, F1Tech)
    
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
    
    print(f"\n✅ RSS Total: {len(articles)} articles fetched")
    
    # Ajouter sources scrapées (WEC, F1 Technical)
    if include_scraped:
        try:
            from .web_scraper import scrape_all_sources
            scraped_articles = scrape_all_sources()
            articles.extend(scraped_articles)
            print(f"✅ Combined Total (RSS + Scraped): {len(articles)} articles\n")
        except ImportError:
            print("⚠️  web_scraper module not found, skipping scraped sources\n")
        except Exception as e:
            print(f"⚠️  Scraping failed: {e}\n")
    else:
        print()
    
    return pd.DataFrame(articles)


def filter_recent_articles(df, hours=168):
    """
    Filtrer articles récents (par défaut 7 jours = 168h)
    
    Args:
        df: DataFrame avec articles
        hours: Nombre d'heures à garder
    
    Returns:
        DataFrame filtré
    """
    
    if df.empty:
        print("⚠️  No articles to filter")
        return df
    
    print(f"🔍 Filtering articles from last {hours} hours ({hours//24} days)...")
    
    # Parser dates (formats variés selon sources) - AVEC UTC
    df['published_dt'] = pd.to_datetime(df['published'], errors='coerce', utc=True)
    
    # Garder articles avec date valide
    df_with_date = df[df['published_dt'].notna()].copy()
    
    # Filtrer par date - AVEC UTC
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
