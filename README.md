# 📰 Motorsport Digest - Automated News Monitoring

> **Système de veille automatisée pour le sport automobile (F1, F2, WEC)**  
> Agrégation intelligente d'articles, résumés IA, et publication hebdomadaire automatique

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-brightgreen.svg)](https://github.com/features/actions)
[![Anthropic Claude](https://img.shields.io/badge/AI-Claude%20Sonnet-orange.svg)](https://www.anthropic.com/)

![Motorsport Digest Banner](https://via.placeholder.com/1200x300/E10600/FFFFFF?text=Motorsport+Digest)

---

## 🎯 Objectif

**Motorsport Digest** est un système de veille automatisée qui :
- 📡 Agrège quotidiennement 20+ sources fiables (F1, WEC, F2, sport auto)
- 🤖 Analyse et score la pertinence des articles (ML simple)
- ✨ Génère des résumés automatiques via IA (Claude API)
- 🌐 Publie une revue hebdomadaire sur GitHub Pages
- ⏱️ Économise ~2h de veille manuelle par semaine

**Cas d'usage** :
- Enrichir connaissances motorsport en continu
- Créer contenu LinkedIn professionnel régulier
- Démontrer compétences Python/IA/Automation
- Se positionner comme expert data motorsport

---

## ✨ Fonctionnalités

### 🔍 Agrégation Intelligente
- **20+ sources RSS** : F1 officiel, FIA WEC, Autosport, The Race, Motorsport.com...
- **Filtrage temporel** : Articles des 7 derniers jours
- **Déduplication** : Évite les doublons automatiquement

### 🧠 Analyse & Scoring
- **Scoring pertinence** : Algorithme ML simple basé sur mots-clés techniques
- **Priorisation** : Focus sur data science, stratégies, analyses techniques
- **Top 15 sélectionnés** : Qualité > quantité

### 🤖 Résumés IA
- **Claude API** (Anthropic) : Résumés concis et factuels
- **Format optimisé** : 100-150 mots par article
- **Ton professionnel** : Adapté audience LinkedIn

### 🌐 Publication Automatique
- **GitHub Pages** : Site web généré automatiquement
- **Design responsive** : Mobile-friendly
- **Archives** : Historique de toutes les éditions

### ⚙️ Automation Complète
- **GitHub Actions** : Exécution hebdomadaire automatique (dimanche 18h UTC)
- **Zero maintenance** : Fonctionne sans intervention
- **Notifications** : Email optionnel si échec

---

## 🏗️ Architecture

```
motorsport-digest/
├── .github/
│   └── workflows/
│       └── weekly-digest.yml       # Automation GitHub Actions
├── veille_motorsport/              # Code source Python
│   ├── __init__.py
│   ├── rss_aggregator.py          # Agrégation flux RSS
│   ├── article_extractor.py       # Extraction contenu complet
│   ├── article_scorer.py          # Scoring pertinence ML
│   ├── ai_summarizer.py           # Résumés Claude API
│   ├── web_generator.py           # Génération HTML
│   └── main.py                    # Pipeline principal
├── docs/                          # GitHub Pages (output)
│   ├── index.html                 # Page d'accueil + archives
│   ├── latest.html                # Dernière édition
│   └── digest-YYYY-MM-DD.html     # Archives datées
├── data/
│   └── veille_motorsport.db       # Base SQLite (historique)
├── requirements.txt               # Dépendances Python
├── .env.example                   # Template variables d'environnement
├── LICENSE                        # Licence MIT
└── README.md                      # Ce fichier
```

---

## 🚀 Installation

### Prérequis

- **Python 3.9+** ([Télécharger](https://www.python.org/downloads/))
- **Compte GitHub** ([Créer](https://github.com/join))
- **API Key Anthropic** ([Obtenir](https://console.anthropic.com/))

### Étape 1 : Cloner le repository

```bash
git clone https://github.com/[votre-username]/motorsport-digest.git
cd motorsport-digest
```

### Étape 2 : Environnement virtuel (recommandé)

```bash
# Créer environnement virtuel
python -m venv venv

# Activer
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### Étape 3 : Installer dépendances

```bash
pip install -r requirements.txt
```

### Étape 4 : Configuration

#### Créer fichier `.env`

```bash
cp .env.example .env
```

#### Éditer `.env` avec votre API key

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
```

### Étape 5 : Test local

```bash
# Tester agrégation RSS
python veille_motorsport/rss_aggregator.py

# Générer digest complet
python veille_motorsport/main.py
```

Si tout fonctionne, un fichier `docs/latest.html` sera créé.

---

## ⚙️ Configuration GitHub Actions

### Étape 1 : Activer GitHub Pages

1. Repository → **Settings** → **Pages**
2. Source : **Deploy from a branch**
3. Branch : **main** / Folder : **/docs**
4. Sauvegarder

Votre site sera accessible à : `https://[username].github.io/motorsport-digest/`

### Étape 2 : Ajouter Secret API Key

1. Repository → **Settings** → **Secrets and variables** → **Actions**
2. Cliquer **New repository secret**
3. Name : `ANTHROPIC_API_KEY`
4. Value : Votre API key Anthropic
5. Add secret

### Étape 3 : Activer Workflow

Le workflow est déjà configuré dans `.github/workflows/weekly-digest.yml`.

**Exécution automatique** :
- Chaque dimanche à 18h00 UTC (19h Paris hiver, 20h été)

**Exécution manuelle** :
1. Repository → **Actions**
2. Sélectionner "Weekly Motorsport Digest"
3. Cliquer **Run workflow**

---

## 📊 Utilisation

### Mode Automatique (recommandé)

Une fois configuré, le système fonctionne automatiquement :

1. **Dimanche 18h UTC** : GitHub Actions génère digest
2. **Dimanche 18h15** : Digest publié sur GitHub Pages
3. **Lundi matin** : Vous consultez le digest
4. **15 min** : Vous créez post LinkedIn avec vos insights

### Mode Manuel

Si vous voulez générer un digest manuellement :

```bash
# Activer environnement virtuel
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Générer digest
python veille_motorsport/main.py

# Consulter résultat
open docs/latest.html  # Mac
xdg-open docs/latest.html  # Linux
start docs/latest.html  # Windows
```

### Personnalisation

#### Ajouter/Retirer sources RSS

Éditer `veille_motorsport/rss_aggregator.py` :

```python
RSS_FEEDS = {
    'Votre_Source': 'https://example.com/rss',
    # Ajouter vos sources ici
}
```

#### Ajuster scoring pertinence

Éditer `veille_motorsport/article_scorer.py` :

```python
KEYWORDS_HIGH_PRIORITY = [
    'data', 'analysis', 'telemetry',
    # Ajouter vos mots-clés
]
```

#### Modifier design HTML

Éditer `veille_motorsport/web_generator.py` :
- Modifier CSS dans la fonction `generate_weekly_digest_html()`
- Personnaliser couleurs, polices, layout

---

## 📝 Publication LinkedIn

### Template Post Hebdomadaire

```
📰 REVUE MOTORSPORT DE LA SEMAINE

Cette semaine dans le sport automobile :

🏎️ F1 : [Titre article le plus pertinent]
[Votre analyse personnelle en 1-2 phrases]

🏁 WEC : [Deuxième sujet intéressant]
[Votre perspective technique]

🔧 TECHNIQUE : [Innovation/analyse technique]
[Votre insight data]

💡 Mon analyse de la semaine :
[Votre réflexion personnelle - CLÉ POUR L'ENGAGEMENT !]

📊 Retrouvez ma revue complète (15 articles analysés) :
👉 https://[votre-username].github.io/motorsport-digest/

#F1 #WEC #Motorsport #DataScience #AnalyseData #SportAutomobile

Quelle actu vous a le plus marqué cette semaine ?
```

### Conseils Publication

✅ **Toujours ajouter votre perspective** (algorithme favorise originalité)  
✅ **Poser une question** en fin de post (encourage engagement)  
✅ **Publier lundi/mardi matin** (meilleure visibilité B2B)  
✅ **Hashtags pertinents** (3-5 maximum)  
✅ **Tag personnes/écuries** si pertinent (sans spam)

---

## 💰 Coûts

### Claude API (Anthropic)

**Estimation mensuelle** :
- 15 articles × 4 semaines = 60 résumés/mois
- ~500 tokens input + 150 tokens output par résumé
- Coût : ~$0.20/mois = **$2.40/an** 💰

**Tarifs Claude** (janvier 2025) :
- Input : $3 / million tokens
- Output : $15 / million tokens

### Infrastructure

- **GitHub Pages** : GRATUIT ✅
- **GitHub Actions** : 2000 min/mois gratuit (largement suffisant) ✅

**TOTAL** : **~$2.50/an** 🎉

---

## 🔧 Dépannage

### Problème : Workflow GitHub Actions échoue

**Solutions** :
1. Vérifier API key dans Secrets
2. Consulter logs : Repository → Actions → Run échoué
3. Vérifier quotas API Anthropic
4. Re-run workflow

### Problème : Pas d'articles récupérés

**Causes possibles** :
1. Sources RSS changées/down
2. Filtrage temporel trop strict
3. Problème réseau

**Debug** :
```bash
python veille_motorsport/rss_aggregator.py
# Vérifier output console
```

### Problème : GitHub Pages ne se met pas à jour

**Solutions** :
1. Settings → Pages → Vérifier configuration
2. Attendre 5-10 min après push
3. Vider cache navigateur
4. Vérifier commit dans branch main

### Problème : Résumés IA de mauvaise qualité

**Solutions** :
1. Améliorer prompt dans `ai_summarizer.py`
2. Augmenter `max_tokens` (actuellement 300)
3. Filtrer mieux les articles upstream (scoring)

---

## 📈 Roadmap

### Version 1.1 (prochainement)

- [ ] Support multi-langues (EN/FR automatique)
- [ ] Newsletter email automatique (optionnel)
- [ ] Intégration Twitter/X pour trends
- [ ] Dashboard analytics (sources les plus citées)
- [ ] Export PDF hebdomadaire

### Version 2.0 (futur)

- [ ] Interface web interactive (React)
- [ ] Recherche full-text dans archives
- [ ] API publique pour accéder aux données
- [ ] Machine Learning avancé (clustering topics)
- [ ] Notifications temps réel (breaking news)

---

## 🤝 Contribution

Les contributions sont bienvenues ! 

**Comment contribuer** :
1. Fork le repository
2. Créer une branche : `git checkout -b feature/amazing-feature`
3. Commit : `git commit -m 'Add amazing feature'`
4. Push : `git push origin feature/amazing-feature`
5. Ouvrir une Pull Request

**Guidelines** :
- Code Python PEP8 compliant
- Ajouter tests si fonctionnalité majeure
- Documenter nouvelles sources RSS
- Tester localement avant PR

---

## 📚 Ressources

### Documentation

- **Feedparser** : https://feedparser.readthedocs.io/
- **Newspaper3k** : https://newspaper.readthedocs.io/
- **Anthropic Claude** : https://docs.anthropic.com/
- **GitHub Actions** : https://docs.github.com/en/actions
- **GitHub Pages** : https://pages.github.com/

### Sources Motorsport Officielles

- **FIA F1** : https://www.fia.com/formula-1
- **Formula1.com** : https://www.formula1.com
- **FIA WEC** : https://www.fiawec.com
- **24h Le Mans** : https://www.lemans.org
- **Autosport** : https://www.autosport.com

### Communauté

- **Questions/Issues** : [GitHub Issues](https://github.com/[username]/motorsport-digest/issues)
- **Discussions** : [GitHub Discussions](https://github.com/[username]/motorsport-digest/discussions)

---

## 📄 Licence

Ce projet est sous licence **MIT**. Voir [LICENSE](LICENSE) pour plus de détails.

Vous êtes libre de :
- ✅ Utiliser commercialement
- ✅ Modifier
- ✅ Distribuer
- ✅ Utiliser en privé

---

## 🙏 Remerciements

### Technologies

- **Python** - Langage principal
- **Anthropic Claude** - Résumés IA
- **GitHub** - Hébergement + automation
- **Feedparser** - Parsing RSS
- **Newspaper3k** - Extraction articles

### Sources d'Inspiration

- **AWS F1 Insights** - Machine Learning en F1
- **The Race** - Analyses techniques de qualité
- **Autosport** - Référence journalisme motorsport

### Communauté Open Source

Merci à tous les contributeurs de bibliothèques Python qui rendent ce projet possible !

---

## 👤 Auteur

**Nicolas Gut**

- 🎨 UI/UX Designer
- 🏎️ Data Analyst Motorsport
- 💼 LinkedIn : [Nicolas Gut] (https://www.linkedin.com/in/nicolasgut/)
- 🐙 GitHub : [@NicolasGut](https://github.com/NicolasGut)
- 🌐 Portfolio : [NicolasGut.github.io](https://NicolasGut.github.io)
- 📧 Email : mail@nicolasgut.com

---

## 📊 Stats Projet

![GitHub stars](https://img.shields.io/github/stars/NicolasGut/motorsport-digest?style=social)
![GitHub forks](https://img.shields.io/github/forks/NicolasGut/motorsport-digest?style=social)
![GitHub issues](https://img.shields.io/github/issues/NicolasGut/motorsport-digest)
![GitHub last commit](https://img.shields.io/github/last-commit/NicolasGut/motorsport-digest)

---

## 💡 FAQ

### Pourquoi Claude API plutôt que GPT-4 ?

- Meilleur rapport qualité/prix pour résumés
- Latence plus faible
- Politique de données plus claire
- (GPT-4 fonctionne aussi, voir code commenté)

### Combien de temps pour setup initial ?

- ~30 minutes si vous suivez le guide
- ~2h si première fois avec GitHub Actions
- Ensuite : 0 maintenance !

### Puis-je utiliser d'autres sources que RSS ?

Oui ! Vous pouvez scraper :
- Twitter/X (API payante)
- Reddit (API gratuite)
- Sites web directement (BeautifulSoup)

### Le système fonctionne-t-il pour d'autres sports ?

Absolument ! Adaptez simplement :
1. Sources RSS (votre sport)
2. Mots-clés scoring (termes spécifiques)
3. Design HTML (couleurs, branding)

### Quelle est la fréquence optimale de publication ?

**Hebdomadaire** est idéal :
- Assez régulier pour algorithme LinkedIn
- Pas trop fréquent (spam)
- Laisse temps pour analyse personnelle

---

<div align="center">

### 🏁 Prêt à lancer votre veille automatisée ?

**[Créer votre repository](https://github.com/new)** · **[Obtenir API Key](https://console.anthropic.com/)** · **[Voir démo](https://votre-username.github.io/motorsport-digest/)**

---

**Fait avec ❤️ et Python par la communauté Data Motorsport**

🏎️ Stay updated, stay ahead! 🏎️

</div>
