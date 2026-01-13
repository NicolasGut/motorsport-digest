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

import time
from datetime import datetime


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
        article.download()
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
        print(f"  ⚠️  Failed to extract {url}: {e}")
        return None


def _extract_with_beautifulsoup(url):
    """Extraction basique avec BeautifulSoup (fallback)"""
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraire titre
        title = ''
        if soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)
        elif soup.find('title'):
            title = soup.find('title').get_text(strip=True)
        
        # Extraire texte (approximatif)
        # Chercher balises article, main, ou tous les paragraphes
        article_tag = soup.find('article') or soup.find('main') or soup
        paragraphs = article_tag.find_all('p')
        text = '\n'.join([p.get_text(strip=True) for p in paragraphs])
        
        return {
            'url': url,
            'title': title,
            'text': text,
            'authors': [],
            'publish_date': None,
            'top_image': '',
            'extracted_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"  ⚠️  Failed to extract {url}: {e}")
        return None


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
