"""
Web Generator Module
Génère les pages HTML du digest hebdomadaire
"""

from datetime import datetime, timedelta
import os
import glob


def generate_weekly_digest_html(summaries_df, week_start=None, week_end=None):
    """
    Générer page HTML digest hebdomadaire
    
    Args:
        summaries_df: DataFrame avec résumés articles
        week_start: Date début semaine (datetime)
        week_end: Date fin semaine (datetime)
    
    Returns:
        HTML complet (string)
    """
    
    if week_start is None:
        week_end = datetime.now()
        week_start = week_end - timedelta(days=7)
    
    html_template = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Revue hebdomadaire motorsport - Analyses data-driven F1, WEC, sport automobile">
    <meta name="author" content="Data Analyst Motorsport">
    <title>Revue Motorsport - {week_start.strftime('%d/%m/%Y')}</title>
    <style>
        /* ============================================
           GLOBAL STYLES
           ============================================ */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
                         system-ui, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
            color: #1a1a1a;
            line-height: 1.6;
        }}
        
        /* ============================================
           HEADER
           ============================================ */
        header {{
            background: linear-gradient(135deg, #E10600, #8B0000);
            color: white;
            padding: 3rem 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(225, 6, 0, 0.3);
        }}
        
        h1 {{
            margin: 0;
            font-size: 2.8rem;
            font-weight: 700;
            letter-spacing: -1px;
        }}
        
        .subtitle {{
            opacity: 0.95;
            margin-top: 0.8rem;
            font-size: 1.1rem;
            font-weight: 400;
        }}
        
        .stats {{
            margin-top: 1.5rem;
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            background: rgba(255, 255, 255, 0.15);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.95rem;
        }}
        
        .stat-item strong {{
            font-weight: 600;
        }}
        
        /* ============================================
           ARTICLES
           ============================================ */
        .article {{
            background: white;
            padding: 2rem;
            margin-bottom: 1.8rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
            border-left: 4px solid transparent;
        }}
        
        .article:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.12);
            border-left-color: #E10600;
        }}
        
        .article-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 1.2rem;
            gap: 1rem;
        }}
        
        .article-title {{
            flex: 1;
            font-size: 1.4rem;
            font-weight: 600;
            color: #1a1a1a;
            margin: 0;
            line-height: 1.3;
        }}
        
        .article-title a {{
            color: #E10600;
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        .article-title a:hover {{
            color: #8B0000;
            text-decoration: underline;
        }}
        
        .relevance-badge {{
            background: linear-gradient(135deg, #E10600, #C00500);
            color: white;
            padding: 0.4rem 0.9rem;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 700;
            white-space: nowrap;
            box-shadow: 0 2px 8px rgba(225, 6, 0, 0.3);
        }}
        
        .relevance-badge.high {{
            background: linear-gradient(135deg, #E10600, #FF0800);
        }}
        
        .relevance-badge.medium {{
            background: linear-gradient(135deg, #FF8C00, #FFA500);
        }}
        
        .relevance-badge.low {{
            background: linear-gradient(135deg, #808080, #A0A0A0);
        }}
        
        .article-meta {{
            display: flex;
            gap: 1rem;
            align-items: center;
            margin-bottom: 1.2rem;
            color: #666;
            font-size: 0.9rem;
            flex-wrap: wrap;
        }}
        
        .source-tag {{
            display: inline-block;
            background: #f0f0f0;
            color: #555;
            padding: 0.3rem 0.8rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 500;
        }}
        
        .date-tag {{
            color: #888;
            font-size: 0.85rem;
        }}
        
        .article-summary {{
            line-height: 1.7;
            color: #333;
            font-size: 1.05rem;
        }}
        
        /* ============================================
           FOOTER
           ============================================ */
        footer {{
            text-align: center;
            margin-top: 4rem;
            padding-top: 2.5rem;
            border-top: 2px solid #ddd;
            color: #666;
        }}
        
        .cta {{
            background: linear-gradient(135deg, #E10600, #8B0000);
            color: white;
            padding: 1.2rem 2.5rem;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            margin-top: 1.5rem;
            font-weight: 600;
            font-size: 1.05rem;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 15px rgba(225, 6, 0, 0.3);
        }}
        
        .cta:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(225, 6, 0, 0.4);
        }}
        
        .footer-meta {{
            margin-top: 2rem;
            font-size: 0.9rem;
            color: #999;
        }}
        
        /* ============================================
           RESPONSIVE
           ============================================ */
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            .article-header {{
                flex-direction: column;
            }}
            
            .stats {{
                flex-direction: column;
                gap: 0.5rem;
            }}
            
            .article {{
                padding: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>📰 Revue Motorsport</h1>
        <p class="subtitle">
            Semaine du {week_start.strftime('%d/%m/%Y')} au {week_end.strftime('%d/%m/%Y')}
        </p>
        <div class="stats">
            <div class="stat-item">
                <strong>{len(summaries_df)}</strong> articles sélectionnés
            </div>
            <div class="stat-item">
                <strong>Sources fiables</strong> F1 · WEC · Technique
            </div>
            <div class="stat-item">
                <strong>Analyse data-driven</strong> + IA
            </div>
        </div>
    </header>
    
    <main>
"""
    
    # Ajouter chaque article
    for idx, row in summaries_df.iterrows():
        # Badge couleur selon score
        score = int(row.get('score', 0))
        badge_class = 'high' if score >= 70 else ('medium' if score >= 40 else 'low')
        
        # Formater date si disponible
        date_str = ''
        if row.get('published'):
            try:
                # Essayer de parser la date
                date_str = f'<span class="date-tag">📅 {row["published"][:10]}</span>'
            except:
                pass
        
        html_template += f"""
        <article class="article">
            <div class="article-header">
                <h2 class="article-title">
                    <a href="{row['url']}" target="_blank" rel="noopener">
                        {row['title']}
                    </a>
                </h2>
                <span class="relevance-badge {badge_class}">{score}</span>
            </div>
            
            <div class="article-meta">
                <span class="source-tag">{row['source']}</span>
                {date_str}
            </div>
            
            <div class="article-summary">
                {row['summary']}
            </div>
        </article>
"""
    
    # Fermer HTML
    html_template += f"""
    </main>
    
    <footer>
        <p style="font-size: 1.1rem; margin-bottom: 1rem;">
            Revue hebdomadaire automatisée · Veille motorsport data-driven
        </p>
        
        <a href="https://github.com/[votre-username]/motorsport-digest" class="cta">
            🏎️ Voir le projet GitHub
        </a>
        
        <p class="footer-meta">
            Généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}
            <br>
            Powered by Python · Claude API · FastF1 · GitHub Actions
        </p>
        
        <p style="margin-top: 2rem; font-size: 0.85rem; color: #aaa;">
            Motorsport Digest · Data Analytics Motorsport
            <br>
            <a href="index.html" style="color: #E10600; text-decoration: none;">
                📚 Voir toutes les archives
            </a>
        </p>
    </footer>
</body>
</html>
"""
    
    return html_template


def save_weekly_digest(html_content, output_dir='docs'):
    """
    Sauvegarder digest dans docs/ pour GitHub Pages
    
    Args:
        html_content: HTML complet
        output_dir: Dossier output (default: docs/)
    """
    
    # Créer dossier si nécessaire
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"💾 Saving digest to {output_dir}/...\n")
    
    # 1. Sauvegarder comme latest.html (toujours à jour)
    latest_path = os.path.join(output_dir, 'latest.html')
    with open(latest_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"  ✅ Saved: latest.html")
    
    # 2. Sauvegarder archive par date
    date_str = datetime.now().strftime('%Y-%m-%d')
    archive_path = os.path.join(output_dir, f'digest-{date_str}.html')
    with open(archive_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"  ✅ Saved: digest-{date_str}.html")
    
    # 3. Générer/mettre à jour index.html
    generate_index_page(output_dir)
    print(f"  ✅ Updated: index.html\n")
    
    print(f"🌐 Access your digest at:")
    print(f"   file://{os.path.abspath(latest_path)}")
    print(f"   (or https://[username].github.io/motorsport-digest/ when deployed)\n")


def generate_index_page(output_dir='docs'):
    """
    Générer page index.html avec liste archives
    
    Args:
        output_dir: Dossier contenant les digests
    """
    
    # Lister tous les digests
    digests = sorted(
        glob.glob(os.path.join(output_dir, 'digest-*.html')),
        reverse=True  # Plus récent en premier
    )
    
    # Générer HTML index
    index_html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Archives revues hebdomadaires motorsport - F1, WEC, analyses data">
    <title>Motorsport Digest - Archives</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
        }
        
        header {
            background: linear-gradient(135deg, #E10600, #8B0000);
            color: white;
            padding: 3rem 2rem;
            border-radius: 15px;
            margin-bottom: 3rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(225, 6, 0, 0.3);
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .tagline {
            font-size: 1.1rem;
            opacity: 0.95;
        }
        
        section {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        
        h2 {
            color: #E10600;
            margin-bottom: 1.5rem;
            font-size: 1.8rem;
        }
        
        .digest-link {
            display: block;
            padding: 1.2rem 1.5rem;
            margin: 0.8rem 0;
            background: linear-gradient(135deg, #f8f8f8, #f0f0f0);
            border-radius: 8px;
            text-decoration: none;
            color: #E10600;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.2s;
            border-left: 4px solid transparent;
        }
        
        .digest-link:hover {
            background: linear-gradient(135deg, #fff, #f8f8f8);
            transform: translateX(5px);
            border-left-color: #E10600;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .digest-link.latest {
            background: linear-gradient(135deg, #E10600, #8B0000);
            color: white;
            font-size: 1.2rem;
        }
        
        .digest-link.latest:hover {
            background: linear-gradient(135deg, #FF0800, #A00600);
        }
        
        footer {
            text-align: center;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 2px solid #ddd;
            color: #666;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 20px 10px;
            }
            
            h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>📰 Motorsport Digest</h1>
        <p class="tagline">
            Revues hebdomadaires · F1 · WEC · Data Analytics
        </p>
    </header>
    
    <section>
        <h2>🔥 Dernière édition</h2>
        <a href="latest.html" class="digest-link latest">
            → Revue de la semaine en cours
        </a>
    </section>
    
    <section>
        <h2>📚 Archives</h2>
"""
    
    # Ajouter liens archives
    if digests:
        for digest_file in digests:
            filename = os.path.basename(digest_file)
            date_str = filename.replace('digest-', '').replace('.html', '')
            
            # Formater date joliment
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                display_date = date_obj.strftime('%d %B %Y')
            except:
                display_date = date_str
            
            index_html += f'        <a href="{filename}" class="digest-link">Semaine du {display_date}</a>\n'
    else:
        index_html += '        <p style="color: #999;">Aucune archive disponible pour le moment.</p>\n'
    
    # Fermer HTML
    index_html += """    </section>
    
    <footer>
        <p>
            Système de veille automatisée motorsport
            <br>
            Powered by Python · Claude API · GitHub Actions
        </p>
        <p style="margin-top: 1rem; font-size: 0.9rem;">
            <a href="https://github.com/[votre-username]/motorsport-digest" 
               style="color: #E10600; text-decoration: none;">
                🐙 Voir le projet sur GitHub
            </a>
        </p>
    </footer>
</body>
</html>
"""
    
    # Sauvegarder
    index_path = os.path.join(output_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)


# ============================================
# TEST MODULE
# ============================================

if __name__ == "__main__":
    import pandas as pd
    
    print("=" * 60)
    print("WEB GENERATOR - TEST")
    print("=" * 60)
    print()
    
    # Données de test
    test_summaries = pd.DataFrame([
        {
            'title': 'F1 Data Revolution: Teams Embrace Machine Learning',
            'url': 'https://example.com/article1',
            'summary': 'Les écuries F1 investissent massivement dans le machine learning pour optimiser leurs stratégies de course. Mercedes et Red Bull utilisent des modèles prédictifs pour simuler des milliers de scénarios et prendre des décisions en temps réel.',
            'score': 85,
            'source': 'F1_Technical',
            'published': '2025-01-13'
        },
        {
            'title': 'WEC 2025: Nouvelles règles techniques',
            'url': 'https://example.com/article2',
            'summary': 'La FIA annonce des changements majeurs dans les règlements techniques LMH pour 2025, visant à équilibrer les performances entre constructeurs et réduire les coûts.',
            'score': 65,
            'source': 'FIA_WEC',
            'published': '2025-01-12'
        },
        {
            'title': 'Hamilton signs new deal',
            'url': 'https://example.com/article3',
            'summary': 'Lewis Hamilton prolonge son contrat avec Mercedes pour deux saisons supplémentaires.',
            'score': 35,
            'source': 'Motorsport_com',
            'published': '2025-01-11'
        },
    ])
    
    # Générer HTML
    print("Generating HTML digest...\n")
    
    html = generate_weekly_digest_html(test_summaries)
    
    print(f"✅ HTML generated ({len(html)} characters)\n")
    
    # Sauvegarder
    save_weekly_digest(html)
    
    print("=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
    print()
    print("Open docs/latest.html in your browser to see the result!")
