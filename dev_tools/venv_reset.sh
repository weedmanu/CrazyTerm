#!/bin/bash
# Script shell pour reinitialiser l'environnement virtuel CrazyTerm hors venv
cd "$(dirname "$0")/.."

# Vérifie si le venv est actif
if [ ! -z "$VIRTUAL_ENV" ]; then
    echo "[INFO] Un venv Python est actif. Ce script doit être lancé hors venv !"
    exit 1
fi

echo
# ==================== [ETAPE 1] Nettoyage des anciens environnements ====================
echo "==================== [ETAPE 1] Nettoyage des anciens environnements ===================="
CLEANED=0
for D in .venv venv env myvenv; do
    if [ -d "$D" ]; then
        echo "[INFO] Suppression de l'environnement virtuel existant $D"
        rm -rf "$D"
        CLEANED=1
    fi
done
if [ $CLEANED -eq 1 ]; then
    echo "[OK] Nettoyage termine."
else
    echo "[OK] Aucun environnement virtuel a supprimer."
fi

echo
# ==================== [ETAPE 2] Creation du nouvel environnement ====================
echo "==================== [ETAPE 2] Creation du nouvel environnement ===================="
VENV_DIR=.venv
echo "Nom du venv : $VENV_DIR"
echo "Chemin complet : $(pwd)/$VENV_DIR"
echo "Python utilise :"
which python3 || which python
python3 --version 2>/dev/null || python --version
python3 -m venv "$VENV_DIR" 2>/dev/null || python -m venv "$VENV_DIR"
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "[ERREUR] La creation du venv a echoue."
    exit 2
fi
echo "[OK] Environnement virtuel cree a $(pwd)/$VENV_DIR."

echo
# ==================== [ETAPE 3] Installation des dependances ====================
echo "==================== [ETAPE 3] Installation des dependances ===================="
. "$VENV_DIR/bin/activate"
echo

echo "[INFO] --> Installation des dependances du projet : requirements.txt"
if [ -f requirements.txt ]; then
    echo "Contenu de requirements.txt :"
    cat requirements.txt
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo "[OK] requirements.txt installe."
else
    echo "[WARN] Aucun requirements.txt trouve."
fi

echo

echo "[INFO] --> Installation des dependances de developpement : dev_requirements.txt"
if [ -f dev_requirements.txt ]; then
    echo "Contenu de dev_requirements.txt :"
    cat dev_requirements.txt
    pip install -r dev_requirements.txt
    echo "[OK] dev_requirements.txt installe."
else
    echo "[INFO] Installation de flake8 et pylint (dependances de base dev)"
    pip install flake8 pylint
    echo "[OK] flake8 et pylint installes."
fi

echo
# ==================== [ETAPE 4] Finalisation ====================
echo "==================== [ETAPE 4] Finalisation ===================="
deactivate
if [ -d "$VENV_DIR" ]; then
    echo
    echo "[OK] L'environnement virtuel CrazyTerm est pret et fonctionnel !"
    echo "Vous pouvez maintenant utiliser le projet en toute securite."
    exit 0
else
    echo
    echo "[ERREUR] La reinitialisation du venv a echoue. Consultez les messages ci-dessus."
    exit 3
fi
