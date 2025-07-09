# CrazyTerm

![CI](https://github.com/weedmanu/CrazyTerm/actions/workflows/ci.yml/badge.svg)

Terminal série avancé avec interface graphique PyQt5.

## 💡 Démarrage rapide (Utilisateur final)

### Installation autonome (RECOMMANDÉ)
```bash
# Téléchargez le projet depuis GitHub
# Puis exécutez :
python build/install_crazyterm.py
```

**Aucune installation préalable requise !**
- Le script détecte/guide l'installation de Python
- Crée automatiquement un environnement isolé
- Installe toutes les dépendances
- Génère l'exécutable `dist/CrazyTerm.exe`

**⚠️ Limitation Windows** : Pour des raisons de sécurité (antivirus), l'exécutable généré ne fonctionnera de façon fiable que sur le PC où il a été créé. Pour une distribution sur d'autres machines, il est recommandé de re-générer l'exécutable sur chaque poste cible.

### Lancement de l'application
Après le build, utilisez directement :
```cmd
dist\CrazyTerm.exe
```

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
```bash
python build/install_crazyterm.py
```
- Installation complète automatique
- Environnement virtuel isolé
- Génération d'exécutable unique
- Aucune dépendance externe requise

## 🧰 Outils de développement
Voir `dev_tools/README.md` pour la liste des scripts de validation et d'automatisation.

## 📄 Dépendances principales
Voir `requirements.txt` :
- PyQt5
- pyserial
- pyinstaller

## ℹ️ Support
- GitHub : https://github.com/[votre-repo]/CrazyTerm
