# Dev Tools – Outils de développement CrazyTerm

Ce dossier regroupe tous les outils de développement, de validation et de maintenance pour le projet CrazyTerm.

## 🧰 Scripts disponibles

### `quality_validator.py`
**But :** Analyse la qualité du code source (architecture, docstrings, typage, robustesse, performance, etc.) et génère un rapport détaillé.
- **Utilisation :**
  ```bash
  python dev_tools/quality_validator.py
  ```
- **Quand l’utiliser ?** Avant chaque commit/push ou pour vérifier la conformité globale du projet.

---

### `pre_build_check.py`
**But :** Checklist automatisée avant toute release ou build : lance le validateur qualité, vérifie les dépendances, la documentation, le packaging et l’état du projet.
- **Utilisation :**
  ```bash
  python dev_tools/pre_build_check.py
  ```
- **Quand l’utiliser ?** Avant de générer un exécutable ou de publier une nouvelle version.

---

### `purge_project.py`
**But :** Purge tous les fichiers temporaires, caches, artefacts de build, logs, etc. (sauf le dossier `build` principal).
- **Utilisation :**
  ```bash
  python dev_tools/purge_project.py
  ```
- **Quand l’utiliser ?** Avant un build propre, pour libérer de l’espace ou repartir d’un état sain.

---

### Scripts de gestion de l’environnement virtuel

#### `venv_reset.bat` (Windows CMD)
**But :** Réinitialise l’environnement virtuel `.venv` à la racine du projet, puis installe les dépendances nécessaires. À lancer hors venv !
- **Utilisation :**
  ```cmd
  dev_tools\venv_reset.bat
  ```

#### `venv_reset.sh` (Linux/Mac)
**But :** Réinitialise l’environnement virtuel `.venv` à la racine du projet, puis installe les dépendances nécessaires. À lancer hors venv !
- **Utilisation :**
  ```bash
  ./dev_tools/venv_reset.sh
  ```

#### `venv_reset.py` (cross-plateforme, usage avancé)
**But :** Réinitialise l’environnement virtuel `.venv` à la racine du projet, en Python pur. Peut être utilisé pour automatiser ou déboguer.
- **Utilisation :**
  ```bash
  python dev_tools/venv_reset.py
  ```

- **Quand les utiliser ?** Si l’environnement virtuel est corrompu, après un changement majeur de dépendances, ou pour repartir d’un environnement propre. Toujours lancer ces scripts hors venv !

---

## Bonnes pratiques

- Avant d’ajouter un nouvel outil, créez le fichier dans `tools/` puis validez avec `quality_validator.py`.
- Utilisez `pre_build_check.py` avant toute publication ou build.
- Purgez régulièrement le projet avec `purge_project.py` pour éviter les conflits de build.
- Maintenez le score qualité à 100% pour garantir la robustesse du projet.

## Notes importantes

- Le validateur découvre automatiquement les outils dans le dossier `tools/`
- Seuls les fichiers commençant par `tool_` et finissant par `.py` sont considérés
- Chaque outil doit avoir une classe correspondante (ex: `tool_calculator.py` → `ToolCalculator`)
- Le score global doit rester à 100% pour maintenir la qualité du projet
