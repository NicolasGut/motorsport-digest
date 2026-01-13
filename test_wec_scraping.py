#!/usr/bin/env python3
"""
Test WEC Scraping
Vérifier que le scraping WEC fonctionne pour votre projet 24h du Mans
"""

from veille_motorsport.web_scraper import scrape_wec_news, scrape_f1technical_news
import sys

print("=" * 70)
print("🏁 TEST WEC SCRAPING - Projet 24h du Mans")
print("=" * 70)
print()

# Test WEC
print("Testing WEC scraping...\n")
wec_articles = scrape_wec_news(max_articles=20)

if wec_articles:
    print(f"\n✅ SUCCESS: {len(wec_articles)} articles WEC récupérés!\n")
    
    print("📰 Aperçu articles WEC:\n")
    for idx, article in enumerate(wec_articles[:5], 1):
        print(f"{idx}. {article['title']}")
        print(f"   URL: {article['link']}")
        print(f"   Date: {article['published']}")
        if article['summary']:
            print(f"   Résumé: {article['summary'][:100]}...")
        print()
    
    # Statistiques
    print("-" * 70)
    print(f"\n📊 Statistiques:")
    print(f"  • Total articles: {len(wec_articles)}")
    print(f"  • Articles avec résumé: {sum(1 for a in wec_articles if a['summary'])}")
    print(f"  • URLs valides: {sum(1 for a in wec_articles if a['link'].startswith('http'))}")
    
    wec_success = True
else:
    print("\n❌ FAIL: Aucun article WEC récupéré")
    print("   → Le site a peut-être changé de structure")
    print("   → Vérifiez manuellement: https://www.fiawec.com/en/news")
    wec_success = False

print("\n" + "=" * 70)

# Test F1 Technical (bonus)
print("\n🔧 TEST F1 TECHNICAL (bonus)...\n")
f1tech_articles = scrape_f1technical_news(max_articles=10)

if f1tech_articles:
    print(f"\n✅ SUCCESS: {len(f1tech_articles)} articles F1 Technical récupérés!\n")
    print("📰 Aperçu:\n")
    for idx, article in enumerate(f1tech_articles[:3], 1):
        print(f"{idx}. {article['title'][:70]}...")
        print(f"   URL: {article['link']}")
        print()
    f1tech_success = True
else:
    print("\n⚠️  Aucun article F1 Technical (pas critique)")
    f1tech_success = False

print("=" * 70)
print("\n🎯 RÉSULTAT FINAL:\n")

if wec_success:
    print("✅ WEC SCRAPING FONCTIONNEL")
    print(f"   → {len(wec_articles)} articles disponibles pour votre veille 24h du Mans")
    print("   → Prêt pour intégration dans le pipeline complet")
    print()
    print("🚀 Prochaine étape: python veille_motorsport/main.py")
    sys.exit(0)
else:
    print("❌ WEC SCRAPING NON FONCTIONNEL")
    print()
    print("Solutions alternatives:")
    print("  1. Vérifier manuellement le site WEC")
    print("  2. Utiliser une source alternative (Autosport WEC section)")
    print("  3. Créer scraper personnalisé basé sur l'inspection du site")
    print()
    print("Note: Le reste du système fonctionnera quand même avec 8 sources RSS")
    sys.exit(1)
