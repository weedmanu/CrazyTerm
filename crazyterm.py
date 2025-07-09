#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CrazySerialTerm - Terminal série avancé
Application de terminal série avec interface graphique PyQt5.

Ce module principal lance l'application CrazyTerm avec une architecture simple et robuste.

Fonctionnalités:
    - Lancement sécurisé de l'application
    - Configuration de l'interface PyQt5
    - Gestion d'erreurs robuste
    - Logging intégré

Auteur: CrazyTerm Development Team
Version: 1.0.0
License: MIT
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtGui import QIcon, QFont

# Ajouter le répertoire du projet au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.main_window import Terminal
from system.utilities import UtilityFunctions

# Charger les paramètres de l'application depuis le JSON
try:
    APP_SETTINGS = UtilityFunctions.load_app_settings()
except Exception as e:
    print(f"Erreur de chargement des paramètres: {e}")
    APP_SETTINGS = {}

def setup_application() -> QApplication:
    """
    Configure l'application avec les paramètres par défaut.
    
    Returns:
        QApplication: L'application configurée avec style et police
        
    Raises:
        RuntimeError: Si l'initialisation de l'application échoue
    """
    try:
        app = QApplication(sys.argv)

        # Définir la police par défaut pour toute l'application
        default_font = QFont("Arial", 12)
        app.setFont(default_font)

        # Appliquer un style Fusion
        app.setStyle(QStyleFactory.create('Fusion'))

        # Appliquer le thème depuis les paramètres
        from interface.theme_manager import apply_theme
        theme = APP_SETTINGS.get('theme', 'sombre')
        apply_theme(theme)
        
        return app
    except Exception as e:
        raise RuntimeError(f"Impossible d'initialiser l'application: {e}")

def setup_logging() -> logging.Logger:
    """
    Configure le système de journalisation (hors historique terminal).
    """
    try:
        log_settings = APP_SETTINGS.get('log_settings', {})
        log_enabled = log_settings.get('enabled', True)
        log_path = log_settings.get('path', 'dev_tools/debug.log')
        if not log_enabled:
            logging.basicConfig(level=logging.CRITICAL)  # Désactive le log
            return logging.getLogger("CrazySerialTerm")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger("CrazySerialTerm")
    except Exception as e:
        raise RuntimeError(f"Impossible de configurer le logging: {e}")

def main() -> None:
    """
    Fonction principale de l'application.
    
    Lance l'application CrazyTerm avec gestion d'erreurs complète.
    
    Raises:
        SystemExit: Code de sortie 1 en cas d'erreur critique
    """
    # Configuration du logging
    logger = setup_logging()
    logger.info("Démarrage de CrazySerialTerm")
    
    try:
        # Configuration de l'application
        app = setup_application()
        
        # Créer et afficher la fenêtre principale
        terminal = Terminal()
        
        # Charger l'icône de l'application
        icon_path: str = UtilityFunctions.resource_path('assets/CrazyTerm.ico')
        if os.path.exists(icon_path):
            terminal.setWindowIcon(QIcon(icon_path))
            logger.debug(f"Icône chargée depuis: {icon_path}")
        else:
            logger.warning(f"Icône non trouvée: {icon_path}")
        
        # Exécuter l'application
        sys.exit(app.exec_())
        
    except ImportError as e:
        logger.critical(f"Dépendance manquante: {str(e)}")
        print(f"ERREUR: Dépendance manquante - {str(e)}")
        print("Veuillez installer les dépendances avec: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Erreur critique lors du démarrage: {str(e)}", exc_info=True)
        print(f"ERREUR CRITIQUE: {str(e)}")
        sys.exit(1)

# Lancer l'application
if __name__ == "__main__":
    main()
