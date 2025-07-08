"""
Gestionnaire des paramètres et configuration pour CrazySerialTerm
Ce module gère la sauvegarde et le chargement des paramètres de l'application.
"""

from typing import Dict, Any
from PyQt5.QtCore import QSettings
import logging

logger = logging.getLogger("CrazySerialTerm")

class SettingsManager:
    """Gestionnaire des paramètres de l'application."""
    
    def __init__(self, app_name: str = "SerialTerminal", settings_name: str = "Settings"):
        """
        Initialise le gestionnaire de paramètres.
        
        Args:
            app_name: Nom de l'application
            settings_name: Nom des paramètres
        """
        self.settings = QSettings(app_name, settings_name)
    
    def save_setting(self, key: str, value: Any) -> None:
        """
        Sauvegarde une valeur de paramètre.
        
        Args:
            key: Clé du paramètre
            value: Valeur à sauvegarder
        """
        try:
            self.settings.setValue(key, value)
            self.settings.sync()
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du paramètre {key}: {str(e)}")
    
    def load_setting(self, key: str, default: Any = None) -> Any:
        """
        Charge une valeur de paramètre.
        
        Args:
            key: Clé du paramètre
            default: Valeur par défaut si le paramètre n'existe pas
            
        Returns:
            Any: Valeur du paramètre
        """
        try:
            value = self.settings.value(key, default)
            return value
        except Exception as e:
            logger.error(f"Erreur lors du chargement du paramètre {key}: {str(e)}")
            return default
    
    def save_all_settings(self, settings_dict: Dict[str, Any]) -> None:
        """
        Sauvegarde un dictionnaire complet de paramètres.
        
        Args:
            settings_dict: Dictionnaire des paramètres à sauvegarder
        """
        try:
            for key, value in settings_dict.items():
                self.settings.setValue(key, value)
            self.settings.sync()
            logger.info("Tous les paramètres sauvegardés")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des paramètres: {str(e)}")
    
    def load_all_settings(self) -> Dict[str, Any]:
        """
        Charge tous les paramètres sauvegardés.
        
        Returns:
            Dict[str, Any]: Dictionnaire des paramètres
        """
        settings_dict = {}
        try:
            for key in self.settings.allKeys():
                settings_dict[key] = self.settings.value(key)
            logger.info("Tous les paramètres chargés")
            return settings_dict
        except Exception as e:
            logger.error(f"Erreur lors du chargement des paramètres: {str(e)}")
            return {}
    