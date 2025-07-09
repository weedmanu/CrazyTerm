#!/bin/bash
# Script shell pour réinitialiser l'environnement virtuel CrazyTerm hors venv (Linux/Mac)
cd "$(dirname "$0")/.." || exit 1

if [ -n "$VIRTUAL_ENV" ]; then
  echo "[INFO] Un venv Python est actif. Fermez ce terminal ou ouvrez-en un nouveau hors venv."
  exit 1
fi

# Suppression de toute trace d'environnement existant
if [ -d .venv ]; then
  echo "[INFO] Suppression de l'environnement virtuel existant (.venv)"
  rm -rf .venv
fi

# Création du nouvel environnement virtuel
python3 -m venv .venv
if [ ! -f .venv/bin/activate ]; then
  echo "[ERREUR] La création du venv a échoué."
  exit 2
fi

# Activation du venv
source .venv/bin/activate

# Installation des dépendances projet
if [ -f requirements.txt ]; then
  echo "[INFO] Installation des dépendances du projet (requirements.txt)"
  pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "[WARN] Aucun requirements.txt trouvé."
fi

# Installation des dépendances de dev
if [ -f dev_tools/dev_requirements.txt ]; then
  echo "[INFO] Installation des dépendances de développement (dev_tools/dev_requirements.txt)"
  pip install -r dev_tools/dev_requirements.txt
else
  echo "[INFO] Installation de flake8 et pylint (dépendances de base dev)"
  pip install flake8 pylint
fi

deactivate

echo
if [ -d .venv ]; then
  echo "[OK] L'environnement virtuel CrazyTerm est prêt et fonctionnel !"
else
  echo "[ERREUR] La réinitialisation du venv a échoué."
fi
