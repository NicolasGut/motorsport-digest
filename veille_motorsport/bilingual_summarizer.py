"""
Bilingual Summarizer - Extension pour ai_summarizer.py
Génère résumés FR + EN en une seule passe
"""

import anthropic
import os
from dotenv import load_dotenv

load_dotenv()


def summarize_article_bilingual(article_text, article_title, article_url):
    """
    Résumer article en FR + EN simultanément avec Claude API
    
    Args:
        article_text: Texte article
        article_title: Titre article
        article_url: URL article
    
    Returns:
        Dict {'summary_fr': str, 'summary_en': str}
    """
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return None
    
    # Tronquer texte si trop long
    max_text_length = 4000
    if len(article_text) > max_text_length:
        article_text = article_text[:max_text_length] + "..."
    
    # Prompt bilingue optimisé avec TITRES traduits
    prompt = f"""Summarize this motorsport article in BOTH French and English, including TRANSLATED TITLES.

Original Title: {article_title}
URL: {article_url}

Article:
{article_text}

Instructions:
- Provide TWO complete entries: one in French, one in English
- TRANSLATE the title into both languages (keep meaning, adapt idioms)
- Each summary: 2-3 sentences, 100-150 words
- Focus on technical, data, business, or strategic insights
- Professional data journalist tone
- No sensationalism

Format your response EXACTLY like this:

FRENCH TITLE:
[Translated title in French]

FRENCH SUMMARY:
[Your French summary here]

ENGLISH TITLE:
[Translated title in English]

ENGLISH SUMMARY:
[Your English summary here]"""
    
    try:
        # Nettoyer proxies
        old_http_proxy = os.environ.pop('HTTP_PROXY', None)
        old_https_proxy = os.environ.pop('HTTPS_PROXY', None)
        old_http_proxy_lower = os.environ.pop('http_proxy', None)
        old_https_proxy_lower = os.environ.pop('https_proxy', None)
        
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=400,  # Plus long pour 2 résumés
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            full_response = message.content[0].text.strip()
            
            # Parser réponse pour extraire FR et EN (avec titres)
            title_fr = article_title  # Fallback
            title_en = article_title  # Fallback
            summary_fr = ""
            summary_en = ""
            
            # Essayer de parser format avec titres
            if "FRENCH TITLE:" in full_response and "ENGLISH TITLE:" in full_response:
                # Split par sections
                parts = full_response.split("ENGLISH TITLE:")
                
                # Partie française
                french_section = parts[0]
                if "FRENCH TITLE:" in french_section and "FRENCH SUMMARY:" in french_section:
                    fr_parts = french_section.split("FRENCH SUMMARY:")
                    title_fr = fr_parts[0].replace("FRENCH TITLE:", "").strip()
                    summary_fr = fr_parts[1].strip() if len(fr_parts) > 1 else ""
                
                # Partie anglaise
                english_section = parts[1] if len(parts) > 1 else ""
                if "ENGLISH SUMMARY:" in english_section:
                    en_parts = english_section.split("ENGLISH SUMMARY:")
                    title_en = en_parts[0].strip()
                    summary_en = en_parts[1].strip() if len(en_parts) > 1 else ""
            
            # Fallback si format non respecté (ancien format)
            elif "FRENCH:" in full_response and "ENGLISH:" in full_response:
                parts = full_response.split("ENGLISH:")
                summary_fr = parts[0].replace("FRENCH:", "").strip()
                summary_en = parts[1].strip() if len(parts) > 1 else ""
            
            else:
                # Dernier fallback
                lines = full_response.split('\n')
                summary_fr = ' '.join(lines[:len(lines)//2])
                summary_en = ' '.join(lines[len(lines)//2:])
            
            return {
                'title_fr': title_fr,
                'title_en': title_en,
                'summary_fr': summary_fr,
                'summary_en': summary_en
            }
        
        finally:
            # Restaurer proxies
            if old_http_proxy:
                os.environ['HTTP_PROXY'] = old_http_proxy
            if old_https_proxy:
                os.environ['HTTPS_PROXY'] = old_https_proxy
            if old_http_proxy_lower:
                os.environ['http_proxy'] = old_http_proxy_lower
            if old_https_proxy_lower:
                os.environ['https_proxy'] = old_https_proxy_lower
    
    except anthropic.AuthenticationError:
        print("❌ Authentication error: Invalid API key")
        return None
    
    except anthropic.APIError as e:
        print(f"❌ API error: {e}")
        return None
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def summarize_batch_bilingual(articles_df, max_articles=20, delay=2):
    """
    Résumer plusieurs articles en mode bilingue
    
    Args:
        articles_df: DataFrame avec articles
        max_articles: Nombre max d'articles
        delay: Délai entre appels
    
    Returns:
        DataFrame avec colonnes 'summary_fr' et 'summary_en'
    """
    
    import pandas as pd
    import time
    from datetime import datetime
    
    if articles_df.empty:
        print("⚠️  No articles to summarize")
        return pd.DataFrame()
    
    # Top articles
    if 'relevance_score' in articles_df.columns:
        top_articles = articles_df.nlargest(max_articles, 'relevance_score')
    else:
        top_articles = articles_df.head(max_articles)
    
    summaries = []
    total = len(top_articles)
    
    print(f"🤖 Generating BILINGUAL AI summaries for {total} articles...\n")
    
    for idx, row in top_articles.iterrows():
        print(f"  [{len(summaries)+1}/{total}] Summarizing (FR+EN)...", end=" ")
        
        try:
            result = summarize_article_bilingual(
                row.get('text', row.get('summary', '')),
                row['title'],
                row['link']
            )
            
            if result and result['summary_fr'] and result['summary_en']:
                summaries.append({
                    'url': row['link'],
                    'title': row['title'],  # Titre original
                    'title_fr': result.get('title_fr', row['title']),  # Titre FR
                    'title_en': result.get('title_en', row['title']),  # Titre EN
                    'summary_fr': result['summary_fr'],
                    'summary_en': result['summary_en'],
                    'score': row.get('relevance_score', 0),
                    'source': row.get('source', ''),
                    'published': row.get('published', ''),
                    'summarized_at': datetime.now().isoformat()
                })
                
                print(f"✅ (FR:{len(result['summary_fr'])} / EN:{len(result['summary_en'])} chars)")
            else:
                print("❌ Failed")
            
            # Rate limiting
            if len(summaries) < total:
                time.sleep(delay)
        
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            break
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✅ Successfully summarized {len(summaries)}/{total} articles\n")
    
    return pd.DataFrame(summaries)


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("=" * 70)
    print("BILINGUAL SUMMARIZER - TEST")
    print("=" * 70)
    
    test_article = """
    Ferrari has announced a major technical partnership with HP for the 2026 
    season. The Audi team principal criticized the branding design as not meeting
    modern standards. This partnership represents a significant shift in Ferrari's
    marketing strategy.
    """
    
    result = summarize_article_bilingual(
        test_article,
        "Ferrari HP branding criticized by Audi official",
        "https://example.com/article"
    )
    
    if result:
        print("\n✅ FRENCH:")
        print(result['summary_fr'])
        print("\n✅ ENGLISH:")
        print(result['summary_en'])
    else:
        print("\n❌ Test failed")
    
    print("\n" + "=" * 70)
