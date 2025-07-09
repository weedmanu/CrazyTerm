# CrazyTerm

Terminal série avancé avec interface graphique PyQt5.

---

## 📑 Sommaire
- [🛠️ Environnement & Dépendances](#-environnement--dépendances)
- [💡 Démarrage rapide](#-démarrage-rapide-utilisateur-final)
- [🖥️ Pour les développeurs](#-pour-les-développeurs)
- [📦 Compilation en exécutable](#-compilation-en-exécutable)
- [🧰 Outils de développement](#-outils-de-développement)
- [🧪 Tests et validation](#-tests-et-validation)
- [🤝 Contribution](#-contribution)
- [ℹ️ Support](#-support)

## 🛠️ Environnement & Dépendances

### Dépendances principales (application)
Voir `dev_tools/requirements.txt` :
- PyQt5
- pyserial
- pyinstaller

### Dépendances outils dev
Voir `dev_tools/dev_requirements.txt` :
- flake8
- pylint
- pytest

> **Note :** L'installation des dépendances de `dev_tools/dev_requirements.txt` n'est nécessaire que si vous souhaitez utiliser les outils de développement (validation qualité, linting, etc.). Le build final ne requiert que les dépendances listées dans `dev_tools/requirements.txt`.

### Installation de l'environnement (recommandé)
```bash
python build/install_crazyterm.py
```
- Installation complète automatique
- Environnement virtuel isolé
- Génération d'exécutable unique
- Aucune dépendance externe requise

### Installation manuelle (avancée)
```bash
python -m venv .venv
.venv\Scripts\activate  # ou source .venv/bin/activate sous Linux/Mac
pip install -r dev_tools/requirements.txt
python crazyterm.py
```

---

## 💡 Démarrage rapide (Utilisateur final)
- Téléchargez le projet depuis GitHub
- Exécutez :
```bash
python build/install_crazyterm.py
```
- Utilisez ensuite :
```cmd
dist\CrazyTerm.exe
```

**Aucune installation préalable requise !**

**⚠️ Limitation Windows** : L'exécutable généré fonctionne de façon fiable uniquement sur le PC où il a été créé. Pour une distribution sur d'autres machines, il est recommandé de re-générer l'exécutable sur chaque poste cible.

---

## 🖥️ Pour les développeurs

### Lancement depuis le code source
```bash
python crazyterm.py
```

### Structure du projet
- `core/` : Cœur de l'application
- `communication/` : Gestion série
- `interface/` : Interface utilisateur
- `system/` : Utilitaires système
- `tools/` : Outils intégrés
- `dev_tools/` : Outils de développement et scripts de validation
- `build/` : Scripts d'installation et de packaging

---

## 📦 Compilation en exécutable

### Installation autonome (recommandé)
```bash
python build/install_crazyterm.py
```

---

## 🧰 Outils de développement
Voir `dev_tools/README.md` pour la liste complète.

Principaux scripts :
- `dev_tools/quality_validator.py` : Validation qualité, robustesse, performance
- `dev_tools/pre_build_check.py` : Checklist avant release/build
- `dev_tools/purge_project.py` : Purge des fichiers temporaires
- `dev_tools/venv_reset.py` : Réinitialisation avancée de l’environnement virtuel

---

## 🧪 Tests et validation
Pour vérifier la qualité du code et la robustesse du projet :
```bash
python dev_tools/quality_validator.py
```

---

## 🤝 Contribution
- Respectez la structure du projet et les conventions de nommage
- Validez la qualité avec `quality_validator.py` avant tout commit
- Documentez tout nouvel outil dans le README concerné

---

## ℹ️ Support
- GitHub : https://github.com/[votre-repo]/CrazyTerm
- Signalez les bugs ou suggestions via les issues GitHub
