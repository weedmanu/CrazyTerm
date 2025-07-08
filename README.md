# CrazyTerm

Terminal série avancé avec interface graphique PyQt5.

## 💡 Démarrage rapide (Utilisateur final)

### Installation autonome (RECOMMANDÉ)
```cmd
# Téléchargez le projet depuis GitHub
# Puis exécutez :
build\install_crazyterm.bat
```

**Aucune installation préalable requise !**
- Le script détecte/guide l'installation de Python
- Crée automatiquement un environnement isolé
- Installe toutes les dépendances
- Génère l'exécutable portable

### Utilisation portable
Après le build, utilisez directement :
```cmd
dist\CrazyTerm.exe
```

Le dossier `dist\portable\` peut être distribué sur n'importe quel PC Windows.

## 🖥️ Pour les développeurs

### Lancement depuis le code source
```bash
python crazyterm.py
```

### Structure du projet
Le projet est organisé en modules clairs :
- `core/` : Cœur de l'application
- `communication/` : Gestion série
- `interface/` : Interface utilisateur
- `system/` : Utilitaires système
- `tools/` : Outils intégrés
- `dev_tools/` : Outils de développement et scripts de validation
- `build/` : Scripts d'installation et de packaging

## 📦 Compilation en exécutable

### Installation autonome (recommandé)
```cmd
build\install_crazyterm.bat
```
- Installation complète automatique
- Environnement virtuel isolé
- Génération d'exécutable portable
- Aucune dépendance externe requise
- Package prêt à distribuer

## 🧰 Outils de développement
Voir `dev_tools/README.md` pour la liste des scripts de validation et d'automatisation.

## 📄 Dépendances principales
Voir `requirements.txt` :
- PyQt5
- pyserial
- pyinstaller

## ℹ️ Support
- GitHub : https://github.com/[votre-repo]/CrazyTerm
