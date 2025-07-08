# Dossier build/

Ce dossier contient les scripts d'installation et de packaging pour CrazyTerm.

## 📦 Script principal

- **install_crazyterm.py** :
    - Installation autonome recommandée pour Windows.
    - Crée un environnement virtuel, installe les dépendances et génère l'exécutable `dist/CrazyTerm.exe`.
    - Purge automatiquement le dossier build après génération.

## 🏁 Utilisation

Ouvrez un terminal et lancez :
```bash
python build/install_crazyterm.py
```

Suivez les instructions à l'écran. Aucun prérequis n'est nécessaire (le script guide l'installation de Python si besoin).

**⚠️ Limitation Windows** : Pour des raisons de sécurité (antivirus), l'exécutable généré ne fonctionnera de façon fiable que sur le PC où il a été créé. Pour une distribution sur d'autres machines, il est recommandé de re-générer l'exécutable sur chaque poste cible.

