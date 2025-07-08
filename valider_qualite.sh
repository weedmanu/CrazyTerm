#!/bin/bash
# Script de validation pour Linux/Mac
echo "🚀 Validation de la qualité du code CrazyTerm..."
echo ""
cd "$(dirname "$0")"
python3 dev_tools/quality_validator.py
read -p "Appuyez sur Entrée pour continuer..."
