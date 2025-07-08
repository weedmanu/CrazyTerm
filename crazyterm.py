#!/usr/bin/env python3
"""
CrazySerialTerm - Terminal série avancé
Application de terminal série avec interface graphique PyQt5.
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtGui import QIcon, QFont

# Ajouter le répertoire du projet au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.main_window import Terminal
from system.utilities import resource_path

def setup_application():
    """
    Configure l'application avec les paramètres par défaut.
    
    Returns:
        QApplication: L'application configurée
    """
    app = QApplication(sys.argv)

    # Définir la police par défaut pour toute l'application
    default_font = QFont("Arial", 12)
    app.setFont(default_font)

    # Appliquer un style Fusion
    app.setStyle(QStyleFactory.create('Fusion'))
    
    return app

def setup_logging():
    """Configure le système de journalisation."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("serial_terminal.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("CrazySerialTerm")

def main():
    """Fonction principale."""
    # Configuration du logging
    logger = setup_logging()
    logger.info("Démarrage de CrazySerialTerm")
    
    try:
        # Configuration de l'application
        app = setup_application()
        
        # Créer et afficher la fenêtre principale
        terminal = Terminal()
        
        # Charger l'icône de l'application
        icon_path = resource_path('assets/CrazySerialTerm.ico')
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
