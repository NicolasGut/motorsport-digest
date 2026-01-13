#!/usr/bin/env python3
"""
Quick Test Script
Vérifie que tout fonctionne correctement avant de lancer le pipeline complet
"""

import sys
import os

def print_section(title):
    """Afficher section"""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()

def test_imports():
    """Tester imports modules"""
    print_section("TEST 1 : Imports des modules")
    
    try:
        import feedparser
        print("✅ feedparser")
    except ImportError as e:
        print(f"❌ feedparser : {e}")
        return False
    
    try:
        import pandas
        print("✅ pandas")
    except ImportError as e:
        print(f"❌ pandas : {e}")
        return False
    
    try:
        import anthropic
        print("✅ anthropic")
    except ImportError as e:
        print(f"❌ anthropic : {e}")
        return False
    
    try:
        import requests
        print("✅ requests")
    except ImportError as e:
        print(f"❌ requests : {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ beautifulsoup4")
    except ImportError as e:
        print(f"❌ beautifulsoup4 : {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv")
    except ImportError as e:
        print(f"❌ python-dotenv : {e}")
        return False
    
    # Optional
    try:
        from newspaper import Article
        print("✅ newspaper (optional)")
    except ImportError:
        print("⚠️  newspaper not installed (will use BeautifulSoup fallback)")
    
    return True

def test_api_key():
    """Tester API key Anthropic"""
    print_section("TEST 2 : API Key Anthropic")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found!")
        print()
        print("Solution :")
        print("  1. Créez un fichier .env à la racine du projet")
        print("  2. Ajoutez : ANTHROPIC_API_KEY=sk-ant-api03-xxxxx")
        print("  3. Obtenez une clé sur : https://console.anthropic.com/")
        print()
        return False
    
    if api_key.startswith("sk-ant-"):
        print(f"✅ API Key found: {api_key[:15]}...{api_key[-5:]}")
        return True
    else:
        print(f"⚠️  API Key found but format looks wrong: {api_key[:20]}...")
        print("   Expected format: sk-ant-api03-...")
        return False

def test_rss_fetch():
    """Tester récupération RSS"""
    print_section("TEST 3 : Récupération RSS (1 source test)")
    
    import feedparser
    
    test_feed = 'https://www.formula1.com/en/latest/all.xml'
    
    print(f"Fetching: {test_feed}...")
    
    try:
        feed = feedparser.parse(test_feed)
        
        if feed.bozo:
            print(f"⚠️  Warning: {feed.bozo_exception}")
        
        if len(feed.entries) > 0:
            print(f"✅ Success: {len(feed.entries)} articles fetched")
            print(f"   Sample: {feed.entries[0].title[:60]}...")
            return True
        else:
            print("❌ No articles found")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_local_modules():
    """Tester imports modules locaux"""
    print_section("TEST 4 : Modules locaux")
    
    try:
        from veille_motorsport.rss_aggregator import fetch_rss_feeds
        print("✅ rss_aggregator")
    except ImportError as e:
        print(f"❌ rss_aggregator : {e}")
        return False
    
    try:
        from veille_motorsport.article_extractor import extract_full_article
        print("✅ article_extractor")
    except ImportError as e:
        print(f"❌ article_extractor : {e}")
        return False
    
    try:
        from veille_motorsport.article_scorer import score_article_relevance
        print("✅ article_scorer")
    except ImportError as e:
        print(f"❌ article_scorer : {e}")
        return False
    
    try:
        from veille_motorsport.ai_summarizer import summarize_article_claude
        print("✅ ai_summarizer")
    except ImportError as e:
        print(f"❌ ai_summarizer : {e}")
        return False
    
    try:
        from veille_motorsport.web_generator import generate_weekly_digest_html
        print("✅ web_generator")
    except ImportError as e:
        print(f"❌ web_generator : {e}")
        return False
    
    return True

def test_directories():
    """Tester structure dossiers"""
    print_section("TEST 5 : Structure dossiers")
    
    dirs_to_check = [
        'veille_motorsport',
        'data',
        'docs',
        '.github/workflows'
    ]
    
    all_ok = True
    
    for dir_name in dirs_to_check:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ (missing)")
            all_ok = False
    
    return all_ok

def main():
    """Lancer tous les tests"""
    
    print()
    print("🏎️" * 30)
    print()
    print("  MOTORSPORT DIGEST - QUICK TEST")
    print()
    print("🏎️" * 30)
    
    results = []
    
    # Tests
    results.append(("Imports", test_imports()))
    results.append(("API Key", test_api_key()))
    results.append(("RSS Fetch", test_rss_fetch()))
    results.append(("Local Modules", test_local_modules()))
    results.append(("Directories", test_directories()))
    
    # Résumé
    print_section("RÉSUMÉ")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} : {test_name}")
        if not result:
            all_passed = False
    
    print()
    print("=" * 60)
    
    if all_passed:
        print()
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print()
        print("Vous pouvez maintenant lancer le pipeline complet :")
        print("  python veille_motorsport/main.py")
        print()
        sys.exit(0)
    else:
        print()
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print()
        print("Résolvez les problèmes ci-dessus avant de lancer le pipeline.")
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()
