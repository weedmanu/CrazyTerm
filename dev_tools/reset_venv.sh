#!/bin/bash
# Réinitialisation de l'environnement virtuel CrazyTerm
cd "$(dirname "$0")/.."
rm -rf .venv
python3 -m venv .venv
