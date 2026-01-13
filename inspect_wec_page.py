#!/usr/bin/env python3
"""
WEC Page Inspector
Outil pour analyser la structure de la page WEC et ajuster le scraper

Usage: python inspect_wec_page.py
"""

import requests
from bs4 import BeautifulSoup
import json
import sys

def inspect_wec_page():
    """Inspecter la page WEC en détail"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'Referer': 'https://www.google.com/',
    }
    
    url = 'https://www.fiawec.com/fr/page/news/30'
    
    print("=" * 80)
    print("WEC PAGE INSPECTOR - Analyse détaillée")
    print("=" * 80)
    print(f"\n📍 URL: {url}\n")
    
    try:
        print("⏳ Fetching page...")
        response = requests.get(url, headers=headers, timeout=20)
        
        print(f"✅ Status: {response.status_code}")
        print(f"📦 Content-Type: {response.headers.get('content-type')}")
        print(f"📏 Size: {len(response.content):,} bytes\n")
        
        if response.status_code != 200:
            print(f"❌ HTTP Error {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # ============================================
        # 1. STRUCTURE GÉNÉRALE
        # ============================================
        
        print("=" * 80)
        print("1️⃣  STRUCTURE GÉNÉRALE")
        print("=" * 80)
        
        print(f"\n📊 Balises principales:")
        print(f"   • <article>: {len(soup.find_all('article'))}")
        print(f"   • <section>: {len(soup.find_all('section'))}")
        print(f"   • <div>: {len(soup.find_all('div'))}")
        print(f"   • <a>: {len(soup.find_all('a', href=True))}")
        
        # ============================================
        # 2. RECHERCHE ARTICLES
        # ============================================
        
        print("\n" + "=" * 80)
        print("2️⃣  RECHERCHE ARTICLES DE NEWS")
        print("=" * 80)
        
        # Stratégie 1 : Articles
        articles = soup.find_all('article')
        print(f"\n📰 Stratégie 1 - <article>: {len(articles)} trouvés")
        if articles:
            for i, art in enumerate(articles[:2], 1):
                title = art.find(['h1', 'h2', 'h3', 'h4'])
                if title:
                    print(f"   {i}. {title.get_text(strip=True)[:70]}...")
        
        # Stratégie 2 : Divs avec classes spécifiques
        print(f"\n📰 Stratégie 2 - Divs avec classes:")
        keywords = ['news', 'article', 'post', 'item', 'card', 'tile', 'entry', 'story']
        for keyword in keywords:
            divs = soup.find_all('div', class_=lambda x: x and keyword in ' '.join(x).lower())
            if divs:
                print(f"   • '{keyword}': {len(divs)} divs")
                if divs[:1]:
                    classes = divs[0].get('class')
                    print(f"      Classes: {classes}")
        
        # Stratégie 3 : Liens vers news
        news_links = soup.find_all('a', href=lambda x: x and ('/news/' in x or '/article/' in x))
        print(f"\n🔗 Stratégie 3 - Liens /news/ ou /article/: {len(news_links)}")
        if news_links:
            print(f"\n   Échantillons:")
            for i, link in enumerate(news_links[:5], 1):
                href = link.get('href')
                text = link.get_text(strip=True)
                if text and len(text) > 10:
                    print(f"   {i}. {text[:60]}...")
                    print(f"      → {href}")
        
        # ============================================
        # 3. ANALYSE JSON / NEXT.JS
        # ============================================
        
        print("\n" + "=" * 80)
        print("3️⃣  DONNÉES JAVASCRIPT / JSON")
        print("=" * 80)
        
        # Next.js data
        next_data = soup.find('script', id='__NEXT_DATA__')
        if next_data:
            print("\n✅ Next.js détecté (__NEXT_DATA__)")
            try:
                data = json.loads(next_data.string)
                print(f"   Keys: {list(data.keys())}")
                
                if 'props' in data and 'pageProps' in data['props']:
                    page_props = data['props']['pageProps']
                    print(f"   pageProps keys: {list(page_props.keys())[:10]}")
                    
                    # Chercher données d'articles
                    if 'news' in page_props:
                        print(f"\n   🎯 TROUVÉ 'news' dans pageProps!")
                        news_data = page_props['news']
                        if isinstance(news_data, list):
                            print(f"      Type: Liste de {len(news_data)} articles")
                            if news_data:
                                print(f"      Premier article keys: {list(news_data[0].keys())[:10]}")
                        elif isinstance(news_data, dict):
                            print(f"      Type: Dict avec keys: {list(news_data.keys())}")
                    
                    # Chercher autres données possibles
                    for key in page_props.keys():
                        if 'article' in key.lower() or 'post' in key.lower() or 'item' in key.lower():
                            print(f"   🔍 Clé intéressante: '{key}' = {type(page_props[key])}")
            
            except Exception as e:
                print(f"   ⚠️  Erreur parsing JSON: {e}")
        else:
            print("\n⚠️  Pas de __NEXT_DATA__ (pas Next.js)")
        
        # Autres scripts JSON
        json_scripts = soup.find_all('script', type='application/json')
        if json_scripts:
            print(f"\n📜 Scripts JSON trouvés: {len(json_scripts)}")
        
        # ============================================
        # 4. RECOMMANDATIONS
        # ============================================
        
        print("\n" + "=" * 80)
        print("4️⃣  RECOMMANDATIONS")
        print("=" * 80)
        
        print("\n💡 Basé sur l'analyse:")
        
        if next_data:
            print("   ✅ Site Next.js détecté")
            print("   → Meilleure stratégie: Extraire données de __NEXT_DATA__")
            print("   → Code à ajouter dans web_scraper.py")
        elif articles:
            print("   ✅ Balises <article> trouvées")
            print("   → Stratégie actuelle devrait fonctionner")
        elif news_links:
            print("   ✅ Liens /news/ trouvés")
            print("   → Utiliser extraction par liens")
        else:
            print("   ⚠️  Structure non standard détectée")
            print("   → Inspection manuelle nécessaire")
        
        # ============================================
        # 5. SAUVEGARDER HTML
        # ============================================
        
        print("\n" + "=" * 80)
        print("5️⃣  SAUVEGARDE")
        print("=" * 80)
        
        output_file = 'wec_page_debug.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"\n💾 Page HTML sauvegardée: {output_file}")
        print("   → Ouvrez ce fichier dans un navigateur pour inspection visuelle")
        print("   → Ou utilisez DevTools pour voir la structure complète")
        
        print("\n" + "=" * 80)
        print("✅ INSPECTION TERMINÉE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    inspect_wec_page()
