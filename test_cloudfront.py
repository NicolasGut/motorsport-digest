#!/usr/bin/env python3
"""
Test extraction avec headers sophistiqués
Vérifier que CloudFront est contourné
"""

from veille_motorsport.article_extractor import extract_full_article
import sys

# URLs CloudFront problématiques à tester
test_urls = [
    ('Autosport', 'https://www.autosport.com/f1/news/f1-2026-efuels-advanced-additives/10789765/'),
    ('Motorsport', 'https://www.motorsport.com/f1/news/cadillac-launches-stealthy-first-f1-livery-for-barcelona-testing/10789753/'),
    ('The Race', 'https://www.the-race.com/formula-1/why-mclaren-believe-2025-errors-will-make-f1-team-better/'),
]

print("=" * 70)
print("TEST EXTRACTION - HEADERS SOPHISTIQUÉS")
print("=" * 70)
print()

success_count = 0
total = len(test_urls)

for source, url in test_urls:
    print(f"Testing [{source}]...")
    print(f"URL: {url}")
    print()
    
    article = extract_full_article(url)
    
    if article and article['text'] and len(article['text']) > 200:
        success_count += 1
        print(f"✅ SUCCESS")
        print(f"   Title: {article['title'][:80]}")
        print(f"   Text length: {len(article['text'])} chars")
        print(f"   Preview: {article['text'][:150]}...")
    else:
        print(f"❌ FAILED - Extraction incomplete or blocked")
        if article:
            print(f"   Title: {article.get('title', 'N/A')}")
            print(f"   Text length: {len(article.get('text', ''))} chars")
    
    print()
    print("-" * 70)
    print()

print("=" * 70)
print(f"RESULTS: {success_count}/{total} successful")
print("=" * 70)

if success_count == total:
    print("🎉 All tests passed! CloudFront bypass working!")
    sys.exit(0)
elif success_count > 0:
    print("⚠️  Partial success - some articles extracted")
    sys.exit(0)
else:
    print("❌ All tests failed - CloudFront still blocking")
    sys.exit(1)
