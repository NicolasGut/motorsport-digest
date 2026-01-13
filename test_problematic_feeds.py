import feedparser
import requests
import ssl

# FIX SSL
ssl._create_default_https_context = ssl._create_unverified_context

# Sources problématiques
feeds = {
    'F1_Official': 'https://www.formula1.com/en/latest/all.xml',
    'FIA_WEC': 'https://www.fiawec.com/en/rss',
    'F1_Technical': 'https://www.f1technical.net/rss',
}

for name, url in feeds.items():
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*60)
    
    # Test 1: Feedparser
    print("\n1. Feedparser test:")
    feed = feedparser.parse(url)
    print(f"   Bozo: {feed.bozo}")
    if feed.bozo:
        print(f"   Error: {feed.bozo_exception}")
    print(f"   Entries: {len(feed.entries)}")
    
    # Test 2: Direct request
    print("\n2. Direct request test:")
    try:
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        print(f"   Length: {len(response.content)} bytes")
        print(f"   First 200 chars: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")