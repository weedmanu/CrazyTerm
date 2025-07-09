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

    @staticmethod
    def load_app_settings() -> dict:
        """
        Charge les paramètres de l'application depuis le fichier config/settings.json.
        
        Returns:
            dict: Dictionnaire des paramètres chargés
        
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ValueError: Si le JSON est invalide
        """
        import json
        config_path = UtilityFunctions.resource_path('config/settings.json')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Fichier de configuration introuvable: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception as e:
                logger.error(f"Erreur lors du chargement du fichier de configuration: {e}")
                raise ValueError(f"Erreur de parsing JSON: {e}")

__all__ = []

