"""
Fonctions utilitaires pour CrazySerialTerm
Ce module contient des fonctions réutilisables dans l'application.
"""

import sys
import os

def resource_path(relative_path):
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
    except Exception:
        # Non packagé, utiliser le répertoire racine du projet
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Remonter au dossier racine (depuis system/ vers la racine)
        base_path = os.path.dirname(current_dir)

    return os.path.join(base_path, relative_path)

