"""
Fonctions utilitaires pour CrazySerialTerm
Ce module contient des fonctions réutilisables dans l'application.
"""

from __future__ import annotations

import sys
import os
import logging
from typing import Any

# Initialisation du logger de module
logger = logging.getLogger(__name__)

class UtilityFunctions:
    """
    Classe utilitaire pour les fonctions de gestion de ressources et chemins dans CrazySerialTerm.
    Toutes les méthodes sont statiques.
    """
    @staticmethod
    def resource_path(relative_path: str) -> str:
        """
        Obtenir le chemin absolu vers la ressource, fonctionne pour dev et pour PyInstaller.
        
        Args:
            relative_path (str): Chemin relatif vers la ressource
        
        Returns:
            str: Chemin absolu vers la ressource
        """
        try:
            # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
            base_path = sys._MEIPASS
        except Exception as e:
            # Non packagé, utiliser le répertoire racine du projet
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # Remonter au dossier racine (depuis system/ vers la racine)
                base_path = os.path.dirname(current_dir)
            except Exception as err:
                logger.error(f"Erreur lors de la résolution du chemin de ressource: {err}")
                raise
        try:
            return os.path.join(base_path, relative_path)
        except Exception as e:
            logger.error(f"Erreur lors de la construction du chemin: {e}")
            raise

__all__ = []

