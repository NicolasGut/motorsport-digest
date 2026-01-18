#!/bin/bash

# 🔄 Script de publication du digest édité
# Usage: ./publish-edited-digest.sh digest-edited-2026-01-18.html

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "=================================================="
echo "🏎️  Publication du Digest Édité"
echo "=================================================="
echo ""

# Vérifier qu'un fichier est fourni
if [ -z "$1" ]; then
    echo -e "${RED}❌ Erreur: Aucun fichier spécifié${NC}"
    echo ""
    echo "Usage: ./publish-edited-digest.sh <fichier-edité>"
    echo "Exemple: ./publish-edited-digest.sh digest-edited-2026-01-18.html"
    echo ""
    exit 1
fi

EDITED_FILE="$1"

# Vérifier que le fichier existe
if [ ! -f "$EDITED_FILE" ]; then
    echo -e "${RED}❌ Erreur: Le fichier $EDITED_FILE n'existe pas${NC}"
    exit 1
fi

echo -e "${YELLOW}📁 Fichier source: $EDITED_FILE${NC}"
echo ""

# Demander confirmation
read -p "Voulez-vous publier ce digest ? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⏸️  Opération annulée${NC}"
    exit 0
fi

# Copier le fichier édité
echo -e "${YELLOW}📝 Copie du digest édité...${NC}"
cp "$EDITED_FILE" docs/latest.html

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur lors de la copie${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Fichier copié${NC}"

# Créer également une archive datée
DATE=$(date +%Y-%m-%d)
cp "$EDITED_FILE" "docs/digest-$DATE.html"
echo -e "${GREEN}✅ Archive créée: docs/digest-$DATE.html${NC}"

# Git add
echo ""
echo -e "${YELLOW}📦 Ajout des fichiers à Git...${NC}"
git add docs/latest.html "docs/digest-$DATE.html"

# Git commit
COMMIT_MSG="📝 Digest édité manuellement ($DATE)"
echo -e "${YELLOW}💬 Commit: $COMMIT_MSG${NC}"
git commit -m "$COMMIT_MSG"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur lors du commit${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Commit réussi${NC}"

# Git push
echo ""
echo -e "${YELLOW}🚀 Push vers GitHub...${NC}"
git push origin main

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur lors du push${NC}"
    exit 1
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Digest publié avec succès !${NC}"
echo "=================================================="
echo ""
echo "🌐 Votre digest sera disponible dans 2-5 minutes sur:"
echo "   https://NicolasGut.github.io/motorsport-digest/"
echo ""
echo "📱 Prochaine étape: Créer votre post LinkedIn !"
echo ""

exit 0
