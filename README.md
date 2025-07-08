# CrazyTerm

Terminal série avancé avec interface graphique PyQt5.

## 🚀 Démarrage rapide

### Installation et utilisation
```cmd
# Cloner le projet
git clone https://github.com/weedmanu/CrazyTerm.git
cd CrazyTerm

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python crazyterm.py
```

### Compilation en exécutable
```cmd
# Utiliser le script d'installation automatique
build\install_crazyterm.bat
```

## 📁 Structure du projet

```
CrazyTerm/
├── crazyterm.py                # 🎯 Application principale
├── requirements.txt            # 📦 Dépendances Python
├── README.md                   # 📖 Documentation
├── assets/
│   └── CrazyTerm.ico          # 🖼️ Icône de l'application
├── build/
│   ├── install_crazyterm.bat  # �️ Script d'installation/build
│   └── README.md              # 📋 Documentation build
├── communication/             # 📡 Module communication série
│   ├── __init__.py
│   └── serial_communication.py
├── core/                      # 🧠 Cœur de l'application
│   ├── __init__.py
│   ├── main_window.py         # Fenêtre principale
│   └── config_manager.py      # Gestionnaire de configuration
├── interface/                 # 🎨 Interface utilisateur
│   ├── __init__.py
│   ├── interface_components.py # Composants UI
│   └── theme_manager.py       # Gestionnaire de thèmes
├── system/                    # ⚙️ Utilitaires système
│   ├── __init__.py
│   ├── custom_exceptions.py   # Exceptions personnalisées
│   ├── error_handling.py      # Gestion d'erreurs
│   ├── memory_optimizer.py    # Optimisation mémoire
│   └── utilities.py           # Utilitaires divers
├── tools/                     # 🔧 Outils intégrés
│   ├── __init__.py
│   ├── tool_checksum.py       # Calculateur checksum
│   └── tool_converter.py      # Convertisseur de données
└── build/                     # 🏗️ Scripts de compilation
    ├── install_crazyterm.bat  # Script d'installation/build
    └── README.md              # Documentation build
```

## 🔧 Fonctionnalités

### Communication série
- ✅ Gestion robuste des connexions série
- ✅ Détection automatique des ports
- ✅ Gestion d'erreurs avancée avec circuit breaker
- ✅ Support des paramètres série complets (baudrate, parité, bits...)

### Interface utilisateur
- ✅ Interface graphique moderne PyQt5
- ✅ Thèmes personnalisables
- ✅ Panneaux de configuration intuitifs
- ✅ Affichage temps réel des données

### Outils intégrés
- ✅ **Calculateur Checksum** : Calcul CRC, MD5, SHA
- ✅ **Convertisseur de données** : Hex, ASCII, décimal, binaire
- ✅ **Gestionnaire mémoire** : Optimisation automatique

### Système
- ✅ Gestion d'erreurs robuste
- ✅ Logging complet
- ✅ Sauvegarde automatique des paramètres
- ✅ Architecture modulaire extensible

## 📋 Modules principaux

### Communication (`communication/`)
- `serial_communication.py` : Gestionnaire série robuste avec thread de lecture

### Core (`core/`)
- `main_window.py` : Fenêtre principale (classe `Terminal`)
- `config_manager.py` : Gestionnaire de configuration

### Interface (`interface/`)
- `interface_components.py` : Composants UI (panneaux de connexion, paramètres)
- `theme_manager.py` : Gestion des thèmes

### System (`system/`)
- `error_handling.py` : Circuit breaker et gestion d'erreurs
- `memory_optimizer.py` : Optimisation mémoire ultra-performante
- `custom_exceptions.py` : Exceptions spécifiques à l'application
- `utilities.py` : Utilitaires système

### Tools (`tools/`)
- `tool_checksum.py` : Calculateur de sommes de contrôle
- `tool_converter.py` : Convertisseur de formats de données

## 🛠️ Installation pour développeurs

### Prérequis
- Python 3.8+
- PyQt5
- pyserial
- pyinstaller (pour la compilation)

### Dépendances
```txt
PyQt5>=5.15.0,<5.16.0
pyserial>=3.5,<4.0
pyinstaller>=6.0,<7.0
```

### Configuration
L'application utilise les mécanismes suivants pour la configuration :
- **QSettings** (système) : Sauvegarde automatique des paramètres dans le registre Windows
- **advanced_settings.json** : Paramètres avancés des panneaux d'interface (généré automatiquement)
- **Logs** : Fichier `serial_terminal.log` pour le suivi des erreurs
- **Valeurs par défaut** : Constantes définies dans le code source

> **Note** : Toute la configuration est gérée automatiquement par l'application, aucune configuration manuelle n'est requise.

## 📄 License

Ce projet est libre.


