# 🚀 Quick Start Guide - Motorsport Digest

Guide rapide pour lancer votre système de veille en **10 minutes**.

---

## ✅ Prérequis

- ✅ Python 3.9+ installé
- ✅ Git installé
- ✅ Compte GitHub
- ✅ Compte Anthropic (API key)

---

## 📦 Installation (5 min)

### 1. Cloner le repository

```bash
git clone https://github.com/[votre-username]/motorsport-digest.git
cd motorsport-digest
```

### 2. Créer environnement virtuel

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Installer dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configuration API Key

```bash
# Créer .env depuis template
cp .env.example .env

# Éditer .env et ajouter votre clé
nano .env  # ou code .env, vim .env, etc.
```

Ajoutez dans `.env` :
```
ANTHROPIC_API_KEY=sk-ant-api03-votre_vraie_cle_ici
```

**Obtenir une clé** : https://console.anthropic.com/

---

## 🧪 Test rapide (2 min)

```bash
# Lancer script de test
python test_quick.py
```

**Si tous les tests passent ✅** → Vous êtes prêt !  
**Si des tests échouent ❌** → Suivez les instructions affichées

---

## 🎬 Premier lancement (3 min)

### Test local complet

```bash
# Générer votre premier digest
python veille_motorsport/main.py
```

**Ce qui va se passer** :
1. Récupération ~100 articles RSS (10-20 sec)
2. Filtrage derniers 7 jours
3. Extraction 50 articles complets (1-2 min)
4. Scoring pertinence
5. Résumés IA des 15 meilleurs (1 min)
6. Génération page HTML

**Résultat** : `docs/latest.html` créé !

### Visualiser le digest

```bash
# macOS
open docs/latest.html

# Linux
xdg-open docs/latest.html

# Windows
start docs/latest.html
```

---

## 🌐 Déploiement GitHub Pages (optionnel)

### 1. Push sur GitHub

```bash
git add .
git commit -m "Initial setup - Motorsport Digest"
git push origin main
```

### 2. Activer GitHub Pages

1. Repository → **Settings** → **Pages**
2. Source : **Deploy from a branch**
3. Branch : **main** / Folder : **/docs**
4. Save

**Votre site sera accessible à** :  
`https://[votre-username].github.io/motorsport-digest/`

### 3. Ajouter Secret API Key

1. Repository → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**
3. Name : `ANTHROPIC_API_KEY`
4. Value : Votre clé API
5. Add secret

### 4. Activer Workflow

Le workflow dans `.github/workflows/weekly-digest.yml` s'exécutera :
- ✅ Automatiquement : **Chaque dimanche à 18h UTC**
- ✅ Manuellement : Actions → Run workflow

---

## 📝 Utilisation hebdomadaire

### Option 1 : Automatique (recommandé)

**Rien à faire !**  
GitHub Actions génère le digest chaque dimanche.

Consultez juste :
- En ligne : `https://[username].github.io/motorsport-digest/`
- Ou recevez notification GitHub

### Option 2 : Manuel

```bash
# Activer venv
source venv/bin/activate

# Générer digest
python veille_motorsport/main.py

# Consulter
open docs/latest.html
```

---

## 🎨 Personnalisation

### Changer nombre d'articles

```bash
# 20 articles au lieu de 15
python veille_motorsport/main.py --max-summaries 20

# Derniers 14 jours
python veille_motorsport/main.py --days 14
```

### Ajouter sources RSS

Éditer `veille_motorsport/rss_aggregator.py` :

```python
RSS_FEEDS = {
    # ... sources existantes
    'Votre_Source': 'https://example.com/rss',
}
```

### Modifier mots-clés scoring

Éditer `veille_motorsport/article_scorer.py` :

```python
KEYWORDS_HIGH_PRIORITY = [
    # Ajouter vos mots-clés
    'votre_mot_cle',
]
```

### Changer design HTML

Éditer `veille_motorsport/web_generator.py` :
- Modifier CSS dans la section `<style>`
- Changer couleurs (actuellement rouge F1 #E10600)

---

## 📊 Publier sur LinkedIn

### Template post hebdomadaire

```
📰 REVUE MOTORSPORT DE LA SEMAINE

Cette semaine dans le sport automobile :

🏎️ [Article 1 titre]
[Votre analyse 1-2 phrases]

🏁 [Article 2 titre]
[Votre perspective]

🔧 [Article 3 technique]
[Votre insight data]

💡 Mon analyse : [VOTRE RÉFLEXION PERSONNELLE]

📊 Retrouvez ma revue complète (15 articles) :
👉 https://[username].github.io/motorsport-digest/

#F1 #WEC #Motorsport #DataScience #Analytics

Quelle actu vous marque le plus ?
```

**Timing optimal** : Lundi ou mardi matin (8h-10h)

**Temps requis** : 15-20 min/semaine

---

## 🐛 Troubleshooting

### Problème : `newspaper3k` ne s'installe pas

```bash
# Solution 1 : Utiliser newspaper4k
pip install newspaper4k

# Solution 2 : Installer dépendances système
brew install libxml2 libxslt  # macOS
```

### Problème : Erreur API Anthropic

```bash
# Vérifier .env
cat .env | grep ANTHROPIC

# Tester clé
python -c "import anthropic; print('OK')"
```

### Problème : GitHub Actions échoue

1. Vérifier Secret API key dans Settings
2. Consulter logs : Actions → Failed run
3. Re-run workflow

### Problème : Pas d'articles récupérés

```bash
# Tester manuellement
python veille_motorsport/rss_aggregator.py

# Augmenter période
python veille_motorsport/main.py --days 14
```

---

## 💰 Coûts

**Anthropic Claude API** :
- 15 articles/semaine × 4 semaines = 60 résumés/mois
- Coût : ~**$0.20/mois** = **$2.40/an** 💸

**Infrastructure** :
- GitHub Pages : GRATUIT ✅
- GitHub Actions : GRATUIT ✅

**TOTAL : ~$2.50/an** 🎉

---

## 📚 Ressources

- **Documentation complète** : `README.md`
- **Guide technique** : `Guide-Veille-Automatisee-Motorsport.md`
- **Aide** : GitHub Issues

---

## ✅ Checklist lancement

- [ ] Python 3.9+ installé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] `.env` créé avec `ANTHROPIC_API_KEY`
- [ ] `test_quick.py` passe tous les tests ✅
- [ ] Premier digest généré localement (`main.py`)
- [ ] `docs/latest.html` existe et s'affiche correctement
- [ ] Repository GitHub créé
- [ ] Code pushé sur GitHub
- [ ] GitHub Pages activé
- [ ] Secret `ANTHROPIC_API_KEY` ajouté
- [ ] Workflow GitHub Actions fonctionne
- [ ] **PRÊT À PUBLIER SUR LINKEDIN !** 🚀

---

**Besoin d'aide ?**  
📧 Créez une Issue sur GitHub  
📖 Consultez le README complet

**Bon monitoring ! 🏎️📰**
