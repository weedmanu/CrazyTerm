# Dev Tools - Outils de développement CrazyTerm

Ce dossier contient les outils de développement et de validation pour le projet CrazyTerm.

## Scripts disponibles

### `quality_validator.py`

Script de validation complète de la qualité du code. Vérifie :
- Architecture du projet
- Qualité du code (8 métriques)
- Performances et optimisations
- Score global détaillé

**Utilisation :**
```bash
python dev_tools/quality_validator.py
```

### `pre_release_check.py`

Checklist automatisée avant publication :
- Lance le validateur de qualité
- Vérifie les dépendances obsolètes
- Contrôle la documentation et le packaging

**Utilisation :**
```bash
python dev_tools/pre_release_check.py
```

### `purge_project.py`

Purge tous les fichiers temporaires, caches, logs, dossiers de build, etc.

**Utilisation :**
```bash
python dev_tools/purge_project.py
```

## Bonnes pratiques

- Avant d’ajouter un nouvel outil, créez le fichier dans `tools/` puis validez avec `quality_validator.py`.
- Utilisez `pre_release_check.py` avant toute publication.

## Notes importantes

- Le validateur découvre automatiquement les outils dans le dossier `tools/`
- Seuls les fichiers commençant par `tool_` et finissant par `.py` sont considérés
- Chaque outil doit avoir une classe correspondante (ex: `tool_calculator.py` → `ToolCalculator`)
- Le score global doit rester à 100% pour maintenir la qualité du projet
