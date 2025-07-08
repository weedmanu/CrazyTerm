# CrazySerialTerm

Terminal série avancé avec interface graphique PyQt5.

## 🚀 Démarrage rapide (Utilisateur final)

### Installation autonome (RECOMMANDÉ)
```cmd
# Téléchargez le projet depuis GitHub
# Puis exécutez :
build\setup_autonomous.bat
```

**Aucune installation préalable requise !**
- Le script détecte/guide l'installation de Python
- Crée automatiquement un environnement isolé
- Installe toutes les dépendances
- Génère l'exécutable portable

### Utilisation portable
Après le build, utilisez directement :
```cmd
dist\CrazySerialTerm.exe
```

Le dossier `dist\portable\` peut être distribué sur n'importe quel PC Windows.

## 🔧 Pour les développeurs

### Lancement depuis le code source
```bash
python crazyserialterm.py
```

### Modification du code
Le projet est organisé en modules clairs :
- `core/` : Cœur de l'application
- `communication/` : Gestion série
- `interface/` : Interface utilisateur
- `system/` : Utilitaires système
- `tools/` : Outils intégrés

## 📦 Compilation en exécutable

### 🎯 Installation autonome (recommandé)
```cmd
build\setup_autonomous.bat
```
**LA SOLUTION TOUT-EN-UN :**
- ✅ Installation complète automatique
- ✅ Environnement virtuel isolé
- ✅ Génération d'exécutable portable
- ✅ Aucune dépendance externe requise
- ✅ Package prêt à distribuer

### ⚡ Build rapide (développeurs)
```cmd
build\build_quick.bat
```
- Pour utilisateurs ayant Python installé
- Build direct sans environnement virtuel

### � Test de l'environnement
```cmd
build\test_environment.bat
```
- Diagnostic complet de l'environnement
- Vérification des dépendances
- Recommandations personnalisées

## 📁 Structure du projet

```
CrazySerialTerm/
├── DEMARRER.bat                # 🚀 Script de démarrage principal
├── INSTRUCTIONS.md             # 📋 Instructions détaillées
├── crazyserialterm.py          # 🎯 Application principale
├── requirements.txt            # 📦 Dépendances Python
├── .gitignore                  # 🚫 Fichiers ignorés par Git
├── README.md                   # 📖 Documentation principale
├── assets/                     # 🖼️ Ressources (icônes)
├── build/                      # 🏗️ Scripts de compilation
│   ├── setup_autonomous.bat    # 🎯 Installation autonome
│   ├── build_quick.bat         # ⚡ Build rapide
│   ├── test_environment.bat    # 🔍 Test environnement
│   └── README.md               # 📋 Documentation build
├── communication/              # 📡 Module communication série
├── core/                       # 🧠 Cœur de l'application
├── interface/                  # 🎨 Interface utilisateur
├── system/                     # ⚙️ Utilitaires système
├── tools/                      # 🔧 Outils intégrés
└── config/                     # 📋 Configuration
```

### 🎯 Fichiers principaux pour utilisateurs

- **`DEMARRER.bat`** : Point d'entrée principal - Lance l'installation/build automatique
- **`INSTRUCTIONS.md`** : Guide détaillé d'utilisation
- **`build/setup_autonomous.bat`** : Script d'installation autonome (recommandé)
- **`dist/CrazySerialTerm.exe`** : Exécutable final (généré après build)
└── docs/                       # Documentation
    ├── health_report.txt        # Rapport de santé
    └── cleanup_log.txt          # Log de nettoyage
```

## Installation

1. **Cloner le projet**
   ```bash
   git clone <repository>
   cd CrazySerialTerm
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application**
   ```bash
   python crazyserialterm.py
   ```

## Compilation en exécutable

### Création complète avec installateur Windows
```cmd
build\build_installer.bat
```
Génère :
- Exécutable sans console
- Script d'installation pour Program Files
- Raccourcis bureau et menu démarrer
- Désinstallateur

### Génération rapide (test)
```cmd
build\quick_build.bat
```

## Fonctionnalités

- ✅ Communication série robuste avec gestion d'erreurs
- ✅ Interface graphique moderne et intuitive
- ✅ Thèmes personnalisables (clair, sombre, hacker)
- ✅ Gestion mémoire optimisée
- ✅ Outils intégrés (calculateur checksum, convertisseur)
- ✅ Architecture modulaire et extensible
- ✅ Sauvegarde automatique des paramètres

## Scripts utilitaires

- `scripts/launcher.py` - Lanceur avec vérifications système
- `scripts/health_check.py` - Diagnostic complet du système
- `scripts/maintenance.py` - Maintenance et réparations automatiques

## Configuration

- `config/settings.ini` - Paramètres principaux de l'application
- `config/advanced.json` - Paramètres avancés et personnalisation

## Support

L'application génère automatiquement des logs et rapports de diagnostic dans le dossier `docs/`.

## Architecture

Le code est organisé en modules logiques :
- **communication** : Gestion de la communication série
- **core** : Cœur de l'application (fenêtre principale, configuration)
- **interface** : Composants d'interface utilisateur
- **system** : Utilitaires système et gestion d'erreurs
- **tools** : Outils intégrés (checksum, convertisseur)
