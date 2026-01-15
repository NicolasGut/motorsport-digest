"""
Bilingual Web Generator
Génère page HTML avec sélecteur FR/EN
"""

from datetime import datetime


def generate_bilingual_html(summaries_df, additional_articles_df=None, output_path='docs/latest.html'):
    """
    Générer page HTML bilingue avec sélecteur
    
    Args:
        summaries_df: DataFrame avec 'summary_fr' et 'summary_en'
        output_path: Chemin fichier HTML
    """
    
    if summaries_df.empty:
        print("⚠️  No summaries to generate HTML")
        return False
    
    # Mapping langues sources
    source_languages = {
        'f1_official': 'EN',
        'racefans': 'EN', 
        'the_race': 'EN',
        'autosport': 'EN',
        'motorsport': 'EN',
        'sportscar365': 'EN',
    }

    # Trier par score
    if 'score' in summaries_df.columns:
        summaries_df = summaries_df.sort_values('score', ascending=False)
    
    # Date génération
    generated_date = datetime.now().strftime('%Y-%m-%d')
    generated_time = datetime.now().strftime('%H:%M')
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Motorsport Digest - {generated_date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #e74c3c;
        }}
        
        h1 {{
            font-size: 2.5em;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .date {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        
        /* LANGUAGE SELECTOR */
        .language-selector {{
            text-align: center;
            margin: 30px 0;
            padding: 15px;
            background: #ecf0f1;
            border-radius: 8px;
        }}
        
        .language-selector button {{
            padding: 10px 25px;
            margin: 0 10px;
            font-size: 1em;
            font-weight: 600;
            border: 2px solid #3498db;
            background: white;
            color: #3498db;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .language-selector button:hover {{
            background: #3498db;
            color: white;
        }}
        
        .language-selector button.active {{
            background: #3498db;
            color: white;
        }}
        
        .article {{
            margin-bottom: 35px;
            padding: 25px;
            background: #fafafa;
            border-left: 4px solid #e74c3c;
            border-radius: 6px;
            transition: transform 0.2s;
        }}
        
        .article:hover {{
            transform: translateX(5px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .article-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }}
        
        .article-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #2c3e50;
            text-decoration: none;
            flex: 1;
        }}
        
        .article-title:hover {{
            color: #e74c3c;
        }}
        
        .article-score {{
            color: #7f8c8d;
            font-size: 0.9em;
            font-weight: 600;
        }}
        
        .article-date {{
            background: #e74c3c;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 15px;
        }}
        
        .article-meta {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 12px;
        }}
        
        .article-summary {{
            color: #34495e;
            line-height: 1.7;
            font-size: 1.05em;
        }}
        
        /* Bilingual content */
        .lang-fr {{ display: block; }}
        .lang-en {{ display: none; }}
        
        body.lang-en .lang-fr {{ display: none; }}
        body.lang-en .lang-en {{ display: block; }}
        
        footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #95a5a6;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}
            
            h1 {{
                font-size: 1.8em;
            }}
            
            .article-header {{
                flex-direction: column;
            }}
            
            .article-date {{
                margin-left: 0;
                margin-top: 10px;
                align-self: flex-start;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏎️ Motorsport Digest</h1>
            <p class="date">{generated_date} - {generated_time}</p>
        </header>
        
        <!-- LANGUAGE SELECTOR -->
        <div class="language-selector">
            <button onclick="switchLanguage('fr')" id="btn-fr" class="active">🇫🇷 Français</button>
            <button onclick="switchLanguage('en')" id="btn-en">🇬🇧 English</button>
        </div>
        
        <main>
"""
    
        # Générer articles
    for idx, row in summaries_df.iterrows():
        score = int(row.get('score', 0))
        source = row.get('source', 'Unknown')
        
        # Récupérer et formater la date de publication
        published_date = row.get('published', None)
        if published_date:
            try:
                if isinstance(published_date, str):
                    # Parser la date depuis différents formats possibles
                    from dateutil import parser
                    date_obj = parser.parse(published_date)
                else:
                    date_obj = published_date
                date_display = date_obj.strftime('%d/%m/%Y')
            except:
                date_display = published_date[:10] if len(str(published_date)) >= 10 else 'N/A'
        else:
            date_display = 'N/A'
        
        # NOUVEAU : Déterminer langue source
        source_key = source.lower().replace('_', '').replace('-', '')
        source_lang = 'EN'  # Défaut
        for key, lang in source_languages.items():
            if key.replace('_', '') in source_key:
                source_lang = lang
                break
        
        # NOUVEAU : Utiliser titres traduits
        title_fr = row.get('title_fr', row.get('title', 'Unknown'))
        title_en = row.get('title_en', row.get('title', 'Unknown'))
        
        html += f"""
            <article class="article">
                <div class="article-header">
                    <!-- MODIFIÉ : Titre FR (visible en mode FR) -->
                    <a href="{row['url']}" target="_blank" class="article-title lang-fr">
                        {title_fr}
                    </a>
                    <!-- NOUVEAU : Titre EN (visible en mode EN) -->
                    <a href="{row['url']}" target="_blank" class="article-title lang-en">
                        {title_en}
                    </a>
                    <span class="article-date">{date_display}</span>
                </div>
                
                <div class="article-meta">
                    <strong>Source:</strong> {source}, {source_lang} • <span class="article-score">Score: {score}</span>
                </div>
                
                <div class="article-summary lang-fr">
                    {row['summary_fr']}
                </div>
                
                <div class="article-summary lang-en">
                    {row['summary_en']}
                </div>
            </article>
"""
    
    # ====================================================================
    # NOUVEAU : SECTION ARTICLES ADDITIONNELS (20 liens)
    # ====================================================================
    if additional_articles_df is not None and not additional_articles_df.empty:
        html += """
        <section style="margin-top: 60px; padding-top: 40px; border-top: 3px solid #e74c3c;">
            <h2 class="lang-fr" style="text-align: center; color: #2c3e50; margin-bottom: 30px;">
                📰 Plus d'informations
            </h2>
            <h2 class="lang-en" style="text-align: center; color: #2c3e50; margin-bottom: 30px;">
                📰 More News
            </h2>
            
            <ul style="list-style: none; padding: 0;">
"""
        
        # Top 20 articles additionnels (après les 20 résumés)
        for idx, row in additional_articles_df.head(20).iterrows():
            source = row.get('source', 'Unknown')
            
            # Déterminer langue source
            source_key = source.lower().replace('_', '').replace('-', '')
            source_lang = 'EN'
            for key, lang in source_languages.items():
                if key.replace('_', '') in source_key:
                    source_lang = lang
                    break
            
            html += f"""
                <li style="margin-bottom: 15px; padding: 15px; background: #f9f9f9; border-radius: 6px;">
                    <a href="{row.get('url', row.get('link', '#'))}" target="_blank" 
                       style="color: #2c3e50; text-decoration: none; font-weight: 500; font-size: 1.05em;">
                        {row.get('title', 'Unknown Article')}
                    </a>
                    <span style="color: #7f8c8d; font-size: 0.9em; margin-left: 10px;">
                        ({source}, {source_lang})
                    </span>
                </li>
"""
        
        html += """
            </ul>
        </section>
"""
    
    html += """
        </main>
        
        <footer>
            <p>Generated automatically with Claude AI • {len(summaries_df)} articles analyzed</p>
            <p><a href="https://github.com/nicolasgut/motorsport-digest" target="_blank">View on GitHub</a></p>
        </footer>
    </div>
    
    <script>
        function switchLanguage(lang) {{
            // Update body class
            document.body.className = 'lang-' + lang;
            
            // Update button states
            document.getElementById('btn-fr').classList.remove('active');
            document.getElementById('btn-en').classList.remove('active');
            document.getElementById('btn-' + lang).classList.add('active');
            
            // Save preference
            localStorage.setItem('preferredLanguage', lang);
        }}
        
        // Load saved preference
        window.addEventListener('DOMContentLoaded', () => {{
            const savedLang = localStorage.getItem('preferredLanguage') || 'fr';
            if (savedLang === 'en') {{
                switchLanguage('en');
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Sauvegarder
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Bilingual HTML generated: {output_path}\n")
    return True


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    import pandas as pd
    
    test_data = pd.DataFrame({
        'title': [
            'Ferrari announces HP partnership',
            'McLaren reveals 2026 strategy'
        ],
        'url': [
            'https://example.com/1',
            'https://example.com/2'
        ],
        'summary_fr': [
            'Ferrari annonce un partenariat majeur avec HP pour 2026.',
            'McLaren dévoile sa stratégie technique pour 2026.'
        ],
        'summary_en': [
            'Ferrari announces major partnership with HP for 2026.',
            'McLaren reveals its technical strategy for 2026.'
        ],
        'score': [85, 78],
        'source': ['Autosport', 'The Race']
    })
    
    generate_bilingual_html(test_data, 'test_bilingual.html')
    print("✅ Test file created: test_bilingual.html")
