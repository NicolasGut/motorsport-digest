"""
Web Scraper Module
Scraping direct pour sources sans flux RSS (WEC, F1 Technical)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import time
import random
import re

# ============================================
# USER AGENTS
# ============================================

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

def get_headers():
    """Headers pour scraping"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/',
    }


# ============================================
# WEC - FIA World Endurance Championship
# ============================================

def scrape_wec_news(max_articles=20):
    """
    Scraper WEC depuis fiawec.com
    URL correcte: https://www.fiawec.com/fr/page/news/30
    
    Returns:
        Liste d'articles format RSS-compatible
    """
    
    print("  → WEC (scraping)...", end=" ")
    
    articles = []
    
    # URL exacte de la page news WEC
    base_url = 'https://www.fiawec.com/fr/page/news/30'
    
    try:
        response = requests.get(base_url, headers=get_headers(), timeout=15)
        
        if response.status_code != 200:
            print(f"⚠️  HTTP {response.status_code}")
            return articles
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Stratégie 1 : Chercher balises <article>
        article_tags = soup.find_all('article', limit=max_articles)
        
        if not article_tags:
            # Stratégie 2 : Chercher divs avec class contenant "news" ou "article"
            article_tags = soup.find_all('div', class_=re.compile(r'(news|article|post|item)', re.I), limit=max_articles)
        
        if not article_tags:
            # Stratégie 3 : Chercher tous les liens vers /news/ ou /article/
            news_links = soup.find_all('a', href=re.compile(r'/(news|article)/'))
            article_tags = news_links[:max_articles]
        
        if not article_tags:
            # Stratégie 4 : Chercher structure spécifique WEC (grille de news)
            article_tags = soup.find_all('div', class_=re.compile(r'(card|box|tile)', re.I), limit=max_articles)
        
        for article in article_tags:
            try:
                # Extraire titre
                title = ''
                title_tag = article.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                if title_tag:
                    title = title_tag.get_text(strip=True)
                elif article.name == 'a':
                    title = article.get_text(strip=True)
                
                if not title or len(title) < 10:
                    continue
                
                # Extraire lien
                link = ''
                link_tag = article.find('a', href=True)
                if link_tag:
                    link = link_tag['href']
                elif article.name == 'a':
                    link = article['href']
                
                # Compléter lien relatif
                if link and not link.startswith('http'):
                    if link.startswith('/'):
                        link = 'https://www.fiawec.com' + link
                    else:
                        link = 'https://www.fiawec.com/' + link
                
                if not link:
                    continue
                
                # Extraire résumé
                summary = ''
                summary_tag = article.find(['p', 'div'], class_=re.compile(r'(summary|excerpt|description|intro|lead)', re.I))
                if summary_tag:
                    summary = summary_tag.get_text(strip=True)
                else:
                    # Prendre premier paragraphe
                    p_tag = article.find('p')
                    if p_tag:
                        summary = p_tag.get_text(strip=True)
                
                # Extraire date (si disponible)
                published = ''
                date_tag = article.find(['time', 'span'], class_=re.compile(r'date', re.I))
                if date_tag:
                    published = date_tag.get('datetime', date_tag.get_text(strip=True))
                
                if not published:
                    # Date par défaut (aujourd'hui)
                    published = datetime.now(timezone.utc).isoformat()
                
                # Ajouter article
                articles.append({
                    'source': 'FIA_WEC',
                    'title': title,
                    'link': link,
                    'published': published,
                    'summary': summary,
                    'fetched_at': datetime.now().isoformat()
                })
            
            except Exception as e:
                continue
        
        if articles:
            print(f"✅ {len(articles)} articles")
        else:
            print(f"⚠️  No articles found (site structure may have changed)")
        
        return articles
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return articles


# ============================================
# F1 TECHNICAL
# ============================================

def scrape_f1technical_news(max_articles=20):
    """
    Scraper F1 Technical depuis f1technical.net
    URL correcte: https://www.f1technical.net/news/
    
    Returns:
        Liste d'articles format RSS-compatible
    """
    
    print("  → F1_Technical (scraping)...", end=" ")
    
    articles = []
    
    # URL exacte de la page news F1 Technical
    base_url = 'https://www.f1technical.net/news/'
    
    try:
        response = requests.get(base_url, headers=get_headers(), timeout=15)
        
        if response.status_code != 200:
            print(f"⚠️  HTTP {response.status_code}")
            return articles
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Stratégie 1 : Chercher balises <article>
        article_tags = soup.find_all('article', limit=max_articles)
        
        if not article_tags:
            # Stratégie 2 : Chercher divs avec class contenant "news" ou "post"
            article_tags = soup.find_all('div', class_=re.compile(r'(news|post|article|item)', re.I), limit=max_articles)
        
        if not article_tags:
            # Stratégie 3 : Topics de forum (si page news redirige vers forum)
            topics = soup.find_all('a', class_=re.compile(r'topictitle', re.I), limit=max_articles)
            if topics:
                article_tags = topics
        
        if not article_tags:
            # Stratégie 4 : Tous les liens dans section news
            news_section = soup.find(['div', 'section'], class_=re.compile(r'news', re.I))
            if news_section:
                article_tags = news_section.find_all('a', href=True)[:max_articles]
            else:
                # Fallback : liens vers /news/ ou contenant "news"
                article_tags = soup.find_all('a', href=re.compile(r'/news/|article|viewtopic'))[:max_articles]
        
        for article in article_tags:
            try:
                # Extraire titre
                title = ''
                if article.name == 'a':
                    title = article.get_text(strip=True)
                else:
                    title_tag = article.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    else:
                        # Fallback : prendre texte du premier lien
                        link_tag = article.find('a')
                        if link_tag:
                            title = link_tag.get_text(strip=True)
                
                if not title or len(title) < 10:
                    continue
                
                # Filtrer titres non pertinents
                skip_keywords = ['login', 'register', 'search', 'profile', 'logout', 'faq', 'forum index', 'board index']
                if any(kw in title.lower() for kw in skip_keywords):
                    continue
                
                # Extraire lien
                link = ''
                if article.name == 'a':
                    link = article['href']
                else:
                    link_tag = article.find('a', href=True)
                    if link_tag:
                        link = link_tag['href']
                
                if not link:
                    continue
                
                # Compléter lien relatif
                if not link.startswith('http'):
                    if link.startswith('/'):
                        link = 'https://www.f1technical.net' + link
                    else:
                        link = 'https://www.f1technical.net/' + link
                
                # Extraire résumé (si disponible)
                summary = ''
                summary_tag = article.find(['p', 'div'], class_=re.compile(r'(summary|excerpt|description|intro)', re.I))
                if summary_tag:
                    summary = summary_tag.get_text(strip=True)
                
                # Date par défaut (F1 Technical ne montre pas toujours les dates clairement)
                published = datetime.now(timezone.utc).isoformat()
                
                # Essayer de trouver date quand même
                date_tag = article.find(['time', 'span'], class_=re.compile(r'date|time', re.I))
                if date_tag:
                    published = date_tag.get('datetime', date_tag.get_text(strip=True))
                
                articles.append({
                    'source': 'F1_Technical',
                    'title': title,
                    'link': link,
                    'published': published,
                    'summary': summary,
                    'fetched_at': datetime.now().isoformat()
                })
            
            except Exception as e:
                continue
        
        if articles:
            print(f"✅ {len(articles)} articles")
        else:
            print(f"⚠️  No articles found (site structure may have changed)")
        
        return articles
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return articles


# ============================================
# FONCTION PRINCIPALE
# ============================================

def scrape_all_sources():
    """
    Scraper toutes les sources web sans RSS
    
    Returns:
        Liste combinée d'articles
    """
    
    all_articles = []
    
    print("\n🕷️  Scraping web sources without RSS...\n")
    
    # WEC
    wec_articles = scrape_wec_news(max_articles=20)
    all_articles.extend(wec_articles)
    
    # Petit délai entre sources (respecter serveurs)
    time.sleep(2)
    
    # F1 Technical
    f1tech_articles = scrape_f1technical_news(max_articles=20)
    all_articles.extend(f1tech_articles)
    
    print(f"\n✅ Total scraped: {len(all_articles)} articles\n")
    
    return all_articles


# ============================================
# TEST MODULE
# ============================================

if __name__ == "__main__":
    import pandas as pd
    
    print("=" * 70)
    print("WEB SCRAPER - TEST")
    print("=" * 70)
    
    articles = scrape_all_sources()
    
    if articles:
        df = pd.DataFrame(articles)
        
        print("\n📰 Sample articles:\n")
        for idx, row in df.head(10).iterrows():
            print(f"{idx+1}. [{row['source']}] {row['title']}")
            print(f"   {row['link']}")
            print()
    else:
        print("\n❌ No articles scraped!")
    
    print("=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
