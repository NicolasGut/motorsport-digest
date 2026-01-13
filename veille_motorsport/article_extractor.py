"""
Article Extractor Module
Extrait le contenu complet des articles depuis leurs URLs
"""

try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    # Fallback sur BeautifulSoup si newspaper pas installé
    from bs4 import BeautifulSoup
    import requests
    NEWSPAPER_AVAILABLE = False
    print("⚠️  newspaper3k/4k not available, using BeautifulSoup fallback")

# Importer requests et BeautifulSoup même si newspaper est disponible
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import random

# ============================================
# HEADERS SOPHISTIQUÉS - Anti-bot detection
# ============================================

# Liste de User-Agents réalistes (rotation aléatoire)
USER_AGENTS = [
    # Chrome Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    
    # Chrome macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    
    # Firefox Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    
    # Firefox macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    
    # Safari macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    
    # Edge Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
]

def get_random_headers():
    """
    Générer headers sophistiqués avec User-Agent aléatoire
    """
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.google.com/',
    }
    return headers


def extract_full_article(url):
    """
    Extraire texte complet d'un article
    
    Args:
        url: URL de l'article
    
    Returns:
        Dict avec contenu article ou None si erreur
    """
    
    if NEWSPAPER_AVAILABLE:
        return _extract_with_newspaper(url)
    else:
        return _extract_with_beautifulsoup(url)


def _extract_with_newspaper(url):
    """Extraction avec newspaper (recommandé)"""
    
    try:
        article = Article(url)
        
        # Configuration avec headers sophistiqués
        article.config.browser_user_agent = random.choice(USER_AGENTS)
        article.config.request_timeout = 15
        article.config.number_threads = 1
        article.config.memoize_articles = False
        
        # Headers additionnels pour newspaper
        article.download(input_html=None, config=article.config)
        article.parse()
        
        return {
            'url': url,
            'title': article.title,
            'text': article.text,
            'authors': article.authors,
            'publish_date': article.publish_date,
            'top_image': article.top_image,
            'extracted_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        # Si newspaper échoue, essayer avec requests + headers
        print(f"  ⚠️  Newspaper failed, trying with custom headers...")
        return _extract_with_custom_headers(url)


def _extract_with_custom_headers(url):
    """
    Extraction avec requests + headers sophistiqués (pour contourner CloudFront)
    """
    try:
        headers = get_random_headers()
        
        # Requête avec headers sophistiqués
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraire titre
        title = ''
        if soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)
        elif soup.find('title'):
            title = soup.find('title').get_text(strip=True)
        
        # Extraire texte (chercher dans plusieurs conteneurs possibles)
        text = ''
        
        # Essayer différents sélecteurs communs
        content_selectors = [
            'article',
            'main',
            '[class*="article-content"]',
            '[class*="post-content"]',
            '[class*="entry-content"]',
            '[itemprop="articleBody"]',
            '.article-body',
            '.story-body',
            '.content',
        ]
        
        for selector in content_selectors:
            container = soup.select_one(selector)
            if container:
                paragraphs = container.find_all('p')
                if paragraphs:
                    text = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
                    if text:
                        break
        
        # Fallback : tous les paragraphes
        if not text:
            paragraphs = soup.find_all('p')
            text = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
        
        # Extraire image
        top_image = ''
        img_tag = soup.find('meta', property='og:image')
        if img_tag:
            top_image = img_tag.get('content', '')
        
        return {
            'url': url,
            'title': title,
            'text': text,
            'authors': [],
            'publish_date': None,
            'top_image': top_image,
            'extracted_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"  ❌ Custom headers failed: {e}")
        return None


def _extract_with_beautifulsoup(url):
    """Extraction basique avec BeautifulSoup (fallback)"""
    return _extract_with_custom_headers(url)


def extract_batch_articles(urls, delay=1, max_articles=None):
    """
    Extraire batch d'articles (respecte rate limits)
    
    Args:
        urls: Liste d'URLs
        delay: Délai entre requêtes (secondes)
        max_articles: Nombre max d'articles (None = tous)
    
    Returns:
        Liste de dicts avec articles extraits
    """
    
    if max_articles:
        urls = urls[:max_articles]
    
    articles = []
    total = len(urls)
    
    print(f"📄 Extracting {total} articles...\n")
    
    for idx, url in enumerate(urls, 1):
        print(f"  [{idx}/{total}] Extracting...", end=" ")
        
        article_data = extract_full_article(url)
        
        if article_data:
            articles.append(article_data)
            print(f"✅ {article_data['title'][:50]}...")
        else:
            print(f"❌ Failed")
        
        # Rate limiting (être respectueux des serveurs)
        if idx < total:
            time.sleep(delay)
    
    print(f"\n✅ Successfully extracted {len(articles)}/{total} articles\n")
    
    return articles


def clean_text(text, max_length=None):
    """
    Nettoyer et normaliser le texte extrait
    
    Args:
        text: Texte brut
        max_length: Longueur max (caractères)
    
    Returns:
        Texte nettoyé
    """
    
    if not text:
        return ""
    
    # Supprimer espaces multiples
    text = ' '.join(text.split())
    
    # Supprimer caractères spéciaux problématiques
    text = text.replace('\x00', '')
    
    # Tronquer si nécessaire
    if max_length and len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text


# ============================================
# TEST MODULE
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("ARTICLE EXTRACTOR - TEST")
    print("=" * 60)
    print()
    
    # URLs de test
    test_urls = [
        'https://www.formula1.com/en/latest/article.html',  # Exemple générique
        'https://www.autosport.com/',
    ]
    
    print(f"Testing extraction on {len(test_urls)} URLs...\n")
    
    # Test extraction simple
    for url in test_urls[:1]:  # Tester juste le premier
        print(f"Testing: {url}\n")
        article = extract_full_article(url)
        
        if article:
            print("✅ Extraction successful!")
            print(f"  Title: {article['title']}")
            print(f"  Text length: {len(article['text'])} characters")
            print(f"  Preview: {article['text'][:200]}...")
        else:
            print("❌ Extraction failed")
        
        print()
    
    print("=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
    print()
    print("Note: Pour tester en conditions réelles, lancez:")
    print("  python veille_motorsport/rss_aggregator.py")
    print("  puis utilisez les URLs récupérées")
