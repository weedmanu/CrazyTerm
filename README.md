# 🖥️ CrazyTerm - Terminal Série Avancé

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-Free-brightgreen.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://github.com/weedmanu/CrazyTerm)

💻 **CrazyTerm** est un terminal série simple et pratique avec interface graphique PyQt5, conçu pour les développeurs et geeks qui travaillent avec des communications série.

## ⚡ Ce que ça fait

### 📡 Communication série
- ✅ **Connexion stable** avec détection des déconnexions USB
- ✅ **Multi-thread** pour pas que ça freeze
- ✅ **Auto-retry** quand ça plante
- ✅ **Tous les paramètres série** (baudrate, parité, etc.)
- ✅ **Détection auto** des ports disponibles
- ✅ **Stats en temps réel** (bytes TX/RX, durée)

### 🎨 Interface sympa
- ✅ **Interface simple** avec PyQt5
- ✅ **Thèmes** (sombre/clair)
- ✅ **Bien organisé** avec des panneaux
- ✅ **Raccourcis clavier** pour aller plus vite
- ✅ **Historique** des commandes

### 🧰 Outils intégrés
- ✅ **🔐 Calculateur Checksum** : CRC16, CRC32, MD5, SHA1, SHA256
- ✅ **🔄 Convertisseur** : Hex ↔ ASCII ↔ Decimal ↔ Binaire
- ✅ **📊 Analyseur** : Pour visualiser les données
- ✅ **⏱️ Envoi répété** : Pour les tests en boucle
- ✅ **🔧 Auto-détection** : Nouveaux outils ajoutés automatiquement

### 🔧 Optimisations
- ✅ **💾 Gestion mémoire** avec nettoyage auto
- ✅ **📊 Buffer intelligent** pour l'affichage fluide
- ✅ **🔢 Limite auto** du nombre de lignes
- ✅ **🔐 Thread-safe** partout

## 📦 Comment installer

### 🔧 Il faut
- **Python 3.8+** (testé avec 3.11)
- **Windows** (pour l'instant)
- **PyQt5** et **pyserial** (installés automatiquement)

### 📥 Installation
```bash
# Cloner le projet
git clone https://github.com/weedmanu/CrazyTerm.git
cd CrazyTerm

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python crazyterm.py
```

### 🔨 Compilation en exécutable
```bash
# Utiliser le script d'installation automatique
build\install_crazyterm.bat
```

## 🏗️ Architecture du projet

```
CrazyTerm/
├── 🎯 crazyterm.py                 # Point d'entrée principal
├── 📦 requirements.txt             # Dépendances Python
├── 📖 README.md                    # Documentation (ce fichier)
├── 🎨 assets/
│   └── CrazyTerm.ico              # Icône de l'application
├── 🛠️ build/
│   ├── install_crazyterm.bat      # Script de compilation
│   └── README.md                  # Documentation build
├── 📡 communication/               # Module communication série
│   ├── __init__.py
│   └── serial_communication.py   # Gestionnaire série multi-thread
├── 🧠 core/                       # Cœur de l'application
│   ├── __init__.py
│   ├── main_window.py            # Fenêtre principale + logique UI
│   └── config_manager.py         # Gestionnaire de configuration
├── 🎭 interface/                  # Interface utilisateur
│   ├── __init__.py
│   ├── interface_components.py   # Composants UI (panneaux, boutons)
│   └── theme_manager.py          # Gestion des thèmes
├── 🔧 system/                     # Utilitaires système
│   ├── __init__.py
│   ├── custom_exceptions.py      # Exceptions personnalisées
│   ├── error_handling.py         # Gestion d'erreurs robuste
│   ├── memory_optimizer.py       # Optimisation mémoire
│   └── utilities.py              # Fonctions utilitaires
└── 🧰 tools/                      # Outils intégrés
    ├── __init__.py
    ├── tool_checksum.py          # Calculateur checksum
    └── tool_converter.py         # Convertisseur de données
```

## 🛠️ Développement

### 🔧 Outils de développement
Le projet inclut des outils pour maintenir la qualité du code :

```bash
# Validation complète de la qualité du code
python dev_tools/quality_validator.py
```

**Fonctionnalités du validateur :**
- ✅ **100% de couverture** sur 8 métriques de qualité
- ✅ **Détection automatique** des nouveaux outils
- ✅ **Validation d'architecture** du projet
- ✅ **Score de performance** et optimisations

**Avant d'ajouter du code :**
1. Lancer la validation pour vérifier le score actuel
2. Développer votre fonctionnalité
3. Re-lancer la validation pour maintenir 100%

Voir `dev_tools/README.md` pour plus de détails.

## 🎯 Utilisation

### 🖥️ Interface principale
L'application se compose de plusieurs panneaux :

1. **📡 Panneau de connexion** : Configuration des paramètres série
2. **💬 Terminal** : Affichage des données reçues/envoyées
3. **⌨️ Panneau d'entrée** : Saisie et envoi de données
4. **🔧 Paramètres avancés** : Options de formatage et outils

### 🔌 Connexion série
1. **Sélectionner le port** dans la liste déroulante
2. **Configurer les paramètres** (baudrate, parité, etc.)
3. **Cliquer sur "Connexion"** pour établir la liaison
4. **Surveiller l'état** via la barre de statut

### 📤 Envoi de données
- **Saisir les données** dans le champ d'entrée
- **Choisir le format** : Texte, Hex, ou Décimal
- **Utiliser les raccourcis** : `Ctrl+Enter` pour envoyer
- **Activer l'envoi répété** pour les tests cycliques

### 🧰 Outils intégrés
- **Calculateur Checksum** : Vérification d'intégrité des données
- **Convertisseur** : Transformation entre différents formats
- **Historique** : Navigation dans les commandes précédentes

## ⚙️ Configuration

### 📋 Paramètres série supportés
- **Baudrate** : 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600
- **Bits de données** : 5, 6, 7, 8
- **Parité** : Aucune, Paire, Impaire, Marque, Espace
- **Bits d'arrêt** : 1, 1.5, 2
- **Contrôle de flux** : Aucun, RTS/CTS, XON/XOFF

### 🎨 Personnalisation
- **Thèmes** : Sombre (défaut), Clair
- **Polices** : Configuration via le menu Affichage
- **Couleurs** : Différentiation TX/RX/Erreurs
- **Filtres** : Affichage sélectif des données

## 🔧 Développement

### 📋 Modules principaux

#### 📡 Communication (`communication/`)
- **`serial_communication.py`** : Gestionnaire série thread-safe avec circuit breaker

#### 🧠 Core (`core/`)
- **`main_window.py`** : Fenêtre principale (classe `Terminal`)
- **`config_manager.py`** : Gestionnaire de configuration (QSettings)

#### 🎭 Interface (`interface/`)
- **`interface_components.py`** : Composants UI (panneaux, widgets)
- **`theme_manager.py`** : Gestion des thèmes et styles

#### 🔧 System (`system/`)
- **`error_handling.py`** : Circuit breaker et retry automatique
- **`memory_optimizer.py`** : Optimisation mémoire ultra-performante
- **`custom_exceptions.py`** : Exceptions spécifiques à l'application
- **`utilities.py`** : Fonctions utilitaires (chemins, ressources)

#### 🧰 Tools (`tools/`)
- **`tool_checksum.py`** : Calculateur de sommes de contrôle
- **`tool_converter.py`** : Convertisseur multi-format

### 📦 Dépendances
```txt
PyQt5>=5.15.0,<5.16.0     # Interface graphique
pyserial>=3.5,<4.0        # Communication série
pyinstaller>=6.0,<7.0     # Compilation en exécutable
```

### 🔧 Configuration technique
- **QSettings** : Sauvegarde automatique des paramètres
- **Multi-threading** : Interface réactive et communication robuste
- **Gestion mémoire** : Limitation automatique et nettoyage intelligent
- **Logging** : Traçabilité complète (fichier `serial_terminal.log`)

## � Fonctionnalités avancées

### 🛡️ Robustesse
- **Circuit breaker** : Protection contre les erreurs répétées
- **Retry automatique** : Reconnexion intelligente
- **Détection USB** : Gestion des déconnexions/reconnexions
- **Thread-safety** : Aucun blocage d'interface

### 🎯 Optimisations
- **📊 Buffer intelligent** : Affichage fluide des données
- **🔢 Limite mémoire** : Gestion automatique de la taille du terminal
- **⚡ Cache optimisé** : Formatage de texte ultra-rapide
- **🧹 Nettoyage automatique** : Libération mémoire proactive

### 🧪 Tests et validation
- **🔧 Tests d'import** : Validation de toutes les dépendances
- **🔌 Tests de connexion** : Vérification des ports série
- **🛡️ Tests de robustesse** : Simulation d'erreurs
- **⚡ Tests de performance** : Optimisation mémoire

## 📊 Statistiques et monitoring

### 📈 Informations en temps réel
- **Bytes transmis/reçus** : Compteurs TX/RX
- **Durée de connexion** : Temps de session
- **Erreurs** : Suivi des problèmes de communication
- **📊 Performance** : Utilisation mémoire et CPU

### 📋 Logging
- **Fichier de log** : `serial_terminal.log`
- **Niveaux** : DEBUG, INFO, WARNING, ERROR, CRITICAL
- **🔄 Rotation** : Gestion automatique de la taille
- **⏰ Traçabilité** : Horodatage de tous les événements

## 🔐 Sécurité

### 🛡️ Gestion des erreurs
- **Exceptions personnalisées** : Hiérarchie d'erreurs claire
- **🔍 Validation d'entrée** : Contrôle des données utilisateur
- **🔄 Isolation des threads** : Protection contre les blocages
- **🔧 Récupération automatique** : Résilience aux pannes

### 🔒 Données
- **🔐 Pas de stockage sensible** : Aucune donnée critique sauvegardée
- **🖥️ Configuration locale** : Paramètres en registre Windows
- **🔒 Logs sécurisés** : Aucune information sensible

## 📞 Support et contribution

### 🤝 Contribution
Les contributions sont les bienvenues ! Processus :
1. 🍴 Fork le projet
2. 🌿 Créer une branche fonctionnalité
3. 💾 Commit avec messages clairs
4. 📤 Push vers votre fork
5. 🔧 Ouvrir une Pull Request

### 📧 Support
- **Issues GitHub** : Rapporter des bugs ou demander des fonctionnalités
- **Documentation** : Consulter ce README et les commentaires du code
- **Logs** : Vérifier le fichier `serial_terminal.log` pour le diagnostic

### 🐛 Résolution de problèmes
- **Problèmes d'import** : Vérifier l'installation des dépendances
- **🔌 Erreurs de connexion** : Vérifier les droits et la disponibilité du port
- **📊 Performance** : Ajuster les paramètres de limite mémoire
- **🎨 Thèmes** : Réinitialiser la configuration si nécessaire

## 📜 License

📄 Ce projet est sous licence libre. Vous êtes libre de l'utiliser, le modifier et le distribuer selon vos besoins.

---

**🎯 CrazyTerm** - Terminal série simple et pratique pour développeurs

💡 *Fait avec ❤️ pour la communauté des développeurs embarqués*
