# Dev Tools - Outils de développement CrazyTerm

Ce dossier contient les outils de développement et de validation pour le projet CrazyTerm.

## Scripts disponibles

### `quality_validator.py`

Script de validation complète de la qualité du code. Utilisé pour s'assurer que le projet maintient des standards de qualité élevés.

**Utilisation :**
```bash
python dev_tools/quality_validator.py
```

**Fonctionnalités :**
- ✅ Validation de l'architecture du projet
- ✅ Analyse de la qualité du code (8 métriques)
- ✅ Vérification des performances et optimisations
- ✅ Score global et détaillé
- ✅ Découverte automatique des fichiers d'outils

**Métriques validées :**
1. **error_handling** - Gestion d'erreurs (try/except/raise)
2. **logging** - Système de logging
3. **documentation** - Docstrings et documentation
4. **type_hints** - Annotations de type
5. **class_structure** - Structure des classes
6. **function_annotations** - Annotations des fonctions
7. **imports_optimization** - Optimisation des imports
8. **code_organization** - Organisation du code

**Objectif :** Maintenir un score de 100% sur toutes les métriques

## Utilisation lors du développement

### Avant d'ajouter un nouvel outil

1. Créer le fichier `tools/tool_nom.py` avec la classe `ToolNom`
2. Lancer la validation : `python dev_tools/quality_validator.py`
3. Corriger les éventuels problèmes de qualité
4. S'assurer que le score reste à 100%

### Avant de committer des changements

1. Lancer la validation complète
2. Vérifier que toutes les métriques sont à 100%
3. Corriger les problèmes identifiés
4. Re-valider avant le commit

## Structure attendue du projet

```
CrazyTerm/
├── core/                 # Composants principaux
├── communication/        # Communication série
├── interface/           # Interface utilisateur
├── system/              # Système et utilitaires
├── tools/               # Outils intégrés (détection automatique)
├── dev_tools/           # Outils de développement
└── assets/              # Ressources
```

## Notes importantes

- Le validateur découvre automatiquement les outils dans le dossier `tools/`
- Seuls les fichiers commençant par `tool_` et finissant par `.py` sont considérés
- Chaque outil doit avoir une classe correspondante (ex: `tool_calculator.py` → `ToolCalculator`)
- Le score global doit rester à 100% pour maintenir la qualité du projet
