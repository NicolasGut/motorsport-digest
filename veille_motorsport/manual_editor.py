"""
Manual Editor - Système d'édition manuelle du digest
Permet d'ajuster le ranking, forcer/retirer articles après génération automatique
"""

import pandas as pd
import json
from pathlib import Path


class DigestEditor:
    """
    Éditeur manuel de digest
    
    Usage:
        editor = DigestEditor('data/motorsport_articles.db')
        
        # Voir top 40 articles
        editor.show_top_articles(40)
        
        # Forcer un article dans le top 20
        editor.force_article_score(url='https://...', new_score=95)
        
        # Bloquer un article (hors sujet)
        editor.block_article(url='https://...')
        
        # Régénérer le digest avec ajustements
        editor.regenerate_digest()
    """
    
    def __init__(self, db_path='data/veille_motorsport.db'):
        self.db_path = db_path
        self.adjustments_file = 'data/manual_adjustments.json'
        self.load_adjustments()
    
    def load_adjustments(self):
        """Charger ajustements manuels sauvegardés"""
        if Path(self.adjustments_file).exists():
            with open(self.adjustments_file, 'r') as f:
                self.adjustments = json.load(f)
        else:
            self.adjustments = {
                'forced_scores': {},  # {url: score}
                'blocked_urls': [],   # [url, url, ...]
                'notes': {}           # {url: note}
            }
    
    def save_adjustments(self):
        """Sauvegarder ajustements"""
        Path('data').mkdir(exist_ok=True)
        with open(self.adjustments_file, 'w') as f:
            json.dump(self.adjustments, f, indent=2)
        print(f"✅ Adjustments saved to {self.adjustments_file}")
    
    def show_top_articles(self, n=40):
        """
        Afficher top N articles avec scores
        
        Args:
            n: Nombre d'articles à afficher
        """
        import sqlite3
        from pathlib import Path
        
        # Vérifier que la base existe
        if not Path(self.db_path).exists():
            print(f"❌ Database not found: {self.db_path}")
            print("   Run the main pipeline first:")
            print("   → python veille_motorsport/main.py")
            print()
            return pd.DataFrame()
        
        conn = sqlite3.connect(self.db_path)
        
        # Vérifier que la table existe
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles'")
        if not cursor.fetchone():
            print("❌ No articles table found")
            print("   Run the main pipeline first:")
            print("   → python veille_motorsport/main.py")
            print()
            conn.close()
            return pd.DataFrame()
        
        query = f"""
            SELECT title, link, relevance_score, source, published
            FROM articles
            ORDER BY relevance_score DESC
            LIMIT {n}
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Appliquer ajustements
        for idx, row in df.iterrows():
            url = row['link']
            
            # Afficher avec ajustements
            original_score = row['relevance_score']
            adjusted_score = self.adjustments['forced_scores'].get(url, original_score)
            is_blocked = url in self.adjustments['blocked_urls']
            note = self.adjustments['notes'].get(url, '')
            
            status = ""
            if is_blocked:
                status = "🚫 BLOCKED"
            elif adjusted_score != original_score:
                status = f"✏️  ADJUSTED ({original_score} → {adjusted_score})"
            
            print(f"\n[{idx+1}] Score: {adjusted_score} {status}")
            print(f"    {row['title']}")
            print(f"    {url}")
            print(f"    Source: {row['source']}")
            if note:
                print(f"    📝 Note: {note}")
        
        return df
    
    def force_article_score(self, url, new_score, note=''):
        """
        Forcer le score d'un article
        
        Args:
            url: URL article
            new_score: Nouveau score (0-100)
            note: Note optionnelle (pourquoi forcé)
        """
        self.adjustments['forced_scores'][url] = new_score
        if note:
            self.adjustments['notes'][url] = note
        
        self.save_adjustments()
        print(f"✅ Article score forced to {new_score}")
        if note:
            print(f"   Note: {note}")
    
    def block_article(self, url, reason=''):
        """
        Bloquer un article (ne sera pas inclus)
        
        Args:
            url: URL article
            reason: Raison du blocage
        """
        if url not in self.adjustments['blocked_urls']:
            self.adjustments['blocked_urls'].append(url)
        
        if reason:
            self.adjustments['notes'][url] = f"BLOCKED: {reason}"
        
        self.save_adjustments()
        print(f"🚫 Article blocked")
        if reason:
            print(f"   Reason: {reason}")
    
    def unblock_article(self, url):
        """Débloquer un article"""
        if url in self.adjustments['blocked_urls']:
            self.adjustments['blocked_urls'].remove(url)
            self.save_adjustments()
            print(f"✅ Article unblocked")
    
    def reset_article(self, url):
        """Reset article aux paramètres auto"""
        if url in self.adjustments['forced_scores']:
            del self.adjustments['forced_scores'][url]
        if url in self.adjustments['blocked_urls']:
            self.adjustments['blocked_urls'].remove(url)
        if url in self.adjustments['notes']:
            del self.adjustments['notes'][url]
        
        self.save_adjustments()
        print(f"✅ Article reset to automatic settings")
    
    def get_adjusted_dataframe(self):
        """
        Obtenir DataFrame avec ajustements appliqués
        
        Returns:
            DataFrame articles avec scores ajustés et articles bloqués retirés
        """
        import sqlite3
        from pathlib import Path
        
        # Vérifier que la base existe
        if not Path(self.db_path).exists():
            print(f"❌ Database not found: {self.db_path}")
            return pd.DataFrame()
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            df = pd.read_sql_query("SELECT * FROM articles", conn)
        except Exception as e:
            print(f"❌ Error reading database: {e}")
            conn.close()
            return pd.DataFrame()
        
        conn.close()
        
        # Appliquer ajustements
        for idx, row in df.iterrows():
            url = row['link']
            
            # Appliquer scores forcés
            if url in self.adjustments['forced_scores']:
                df.at[idx, 'relevance_score'] = self.adjustments['forced_scores'][url]
        
        # Retirer articles bloqués
        df = df[~df['link'].isin(self.adjustments['blocked_urls'])]
        
        # Re-trier
        df = df.sort_values('relevance_score', ascending=False).reset_index(drop=True)
        
        return df
    
    def regenerate_digest(self):
        """
        Régénérer le digest avec ajustements manuels
        """
        from bilingual_summarizer import summarize_batch_bilingual
        from bilingual_web_generator import generate_bilingual_html
        
        print("🔄 Regenerating digest with manual adjustments...")
        
        # Charger articles ajustés
        df = self.get_adjusted_dataframe()
        
        print(f"  📊 {len(df)} articles (after blocking)")
        
        # Générer résumés pour top 20
        summaries = summarize_batch_bilingual(df, max_articles=20, delay=1)
        
        # Articles additionnels (21-40)
        additional = df.iloc[20:40] if len(df) > 20 else None
        
        # Générer HTML
        generate_bilingual_html(summaries, additional, output_path='docs/latest.html')
        
        print("✅ Digest regenerated with your adjustments!")


# ============================================
# INTERFACE CLI INTERACTIVE
# ============================================

def interactive_editor():
    """Interface CLI pour éditer le digest"""
    
    editor = DigestEditor()
    
    print("=" * 70)
    print("📝 MOTORSPORT DIGEST - MANUAL EDITOR")
    print("=" * 70)
    print()
    
    while True:
        print("\nCommands:")
        print("  1. Show top 40 articles")
        print("  2. Force article score")
        print("  3. Block article (hors sujet)")
        print("  4. Unblock article")
        print("  5. Reset article")
        print("  6. Regenerate digest")
        print("  7. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            n = input("How many articles? [40]: ").strip() or '40'
            editor.show_top_articles(int(n))
        
        elif choice == '2':
            url = input("Article URL: ").strip()
            score = int(input("New score (0-100): ").strip())
            note = input("Note (optional): ").strip()
            editor.force_article_score(url, score, note)
        
        elif choice == '3':
            url = input("Article URL to block: ").strip()
            reason = input("Reason (optional): ").strip()
            editor.block_article(url, reason)
        
        elif choice == '4':
            url = input("Article URL to unblock: ").strip()
            editor.unblock_article(url)
        
        elif choice == '5':
            url = input("Article URL to reset: ").strip()
            editor.reset_article(url)
        
        elif choice == '6':
            confirm = input("Regenerate digest? (y/n): ").strip().lower()
            if confirm == 'y':
                editor.regenerate_digest()
        
        elif choice == '7':
            print("👋 Goodbye!")
            break


if __name__ == "__main__":
    interactive_editor()
