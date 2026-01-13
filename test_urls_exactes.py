#!/usr/bin/env python3
"""
Test rapide des URLs exactes WEC et F1 Technical
"""

import requests
from bs4 import BeautifulSoup

# Headers basiques
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("=" * 70)
print("TEST URLs EXACTES")
print("=" * 70)

# Test WEC
print("\n1. Testing WEC:")
print("   URL: https://www.fiawec.com/fr/page/news/30")

try:
    response = requests.get('https://www.fiawec.com/fr/page/news/30', headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Chercher articles
        articles = soup.find_all('article')
        print(f"   <article> tags: {len(articles)}")
        
        # Chercher divs news
        news_divs = soup.find_all('div', class_=lambda x: x and ('news' in x.lower() or 'item' in x.lower() or 'card' in x.lower()))
        print(f"   News divs: {len(news_divs)}")
        
        # Chercher titres
        titles = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        print(f"   Headings found: {len(titles)}")
        
        if titles:
            print(f"   Sample title: {titles[0].get_text(strip=True)[:70]}...")
        
        # Chercher liens
        links = soup.find_all('a', href=True)
        news_links = [l for l in links if '/news/' in l['href'] or '/article/' in l['href']]
        print(f"   News links: {len(news_links)}")
        
        if news_links:
            print(f"   Sample link: {news_links[0]['href']}")
            print(f"   Link text: {news_links[0].get_text(strip=True)[:60]}...")
        
        if articles or news_divs or news_links:
            print("   ✅ Structure détectable - Scraping possible!")
        else:
            print("   ⚠️  Structure non standard - Ajustements nécessaires")
    else:
        print(f"   ❌ HTTP Error {response.status_code}")

except Exception as e:
    print(f"   ❌ Error: {e}")

# Test F1 Technical
print("\n2. Testing F1 Technical:")
print("   URL: https://www.f1technical.net/news/")

try:
    response = requests.get('https://www.f1technical.net/news/', headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Chercher articles
        articles = soup.find_all('article')
        print(f"   <article> tags: {len(articles)}")
        
        # Chercher posts/items
        posts = soup.find_all('div', class_=lambda x: x and ('post' in x.lower() or 'news' in x.lower() or 'item' in x.lower()))
        print(f"   Post divs: {len(posts)}")
        
        # Chercher titres
        titles = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        print(f"   Headings found: {len(titles)}")
        
        if titles:
            print(f"   Sample title: {titles[0].get_text(strip=True)[:70]}...")
        
        # Chercher liens
        links = soup.find_all('a', href=True)
        news_links = [l for l in links if '/news/' in l['href'] or 'article' in l['href']]
        print(f"   News links: {len(news_links)}")
        
        if news_links:
            print(f"   Sample link: {news_links[0]['href']}")
            print(f"   Link text: {news_links[0].get_text(strip=True)[:60]}...")
        
        if articles or posts or news_links:
            print("   ✅ Structure détectable - Scraping possible!")
        else:
            print("   ⚠️  Structure non standard - Ajustements nécessaires")
    else:
        print(f"   ❌ HTTP Error {response.status_code}")

except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("\n💡 Prochaine étape:")
print("   python test_wec_scraping.py")
print("=" * 70)
