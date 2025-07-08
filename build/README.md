# Dossier build/

Ce dossier contient les scripts d'installation et de packaging pour CrazyTerm.

## 📦 Scripts principaux

- **install_crazyterm.bat** :
    - Installation autonome recommandée pour Windows.
    - Crée un environnement virtuel, installe les dépendances et génère l'exécutable portable `CrazyTerm.exe`.
    - Place le résultat dans `dist/` et un package prêt à distribuer dans `dist/portable/`.

## 🏁 Utilisation

Ouvrez un terminal Windows et lancez :
```cmd
build\install_crazyterm.bat
```

Suivez les instructions à l'écran. Aucun prérequis n'est nécessaire (le script guide l'installation de Python si besoin).

