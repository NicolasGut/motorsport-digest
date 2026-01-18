"""
Veille Motorsport - SystÃ¨me de veille automatisÃ©e
Pour F1, F2, WEC et sport automobile

Package principal contenant tous les modules de veille.
"""

__version__ = "1.0.0"
__author__ = "Votre Nom"

# Imports principaux pour faciliter l'utilisation
from .rss_aggregator import fetch_rss_feeds, filter_recent_articles, save_to_database
from .article_extractor import extract_full_article, extract_batch_articles
from .article_scorer import score_article_v2, rank_articles, get_top_articles
from .ai_summarizer import summarize_article_claude, summarize_batch
from .web_generator import generate_weekly_digest_html, save_weekly_digest
from .web_scraper import scrape_wec_news, scrape_f1technical_news, scrape_all_sources

__all__ = [
    'fetch_rss_feeds',
    'filter_recent_articles',
    'save_to_database',
    'extract_full_article',
    'extract_batch_articles',
    'score_article_v2',
    'rank_articles',
    'get_top_articles',
    'summarize_article_claude',
    'summarize_batch',
    'generate_weekly_digest_html',
    'save_weekly_digest',
    'scrape_wec_news',
    'scrape_f1technical_news',
    'scrape_all_sources',
]
