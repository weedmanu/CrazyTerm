"""
Module de gestion des paramètres et de la configuration pour CrazySerialTerm.
Ce module fournit un gestionnaire professionnel pour la sauvegarde, le chargement et la réinitialisation
 des paramètres de l'application, avec gestion d'erreur robuste et journalisation.
Toutes les méthodes sont documentées et typées selon les standards professionnels.
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from PyQt5.QtCore import QSettings
import logging

logger = logging.getLogger("CrazySerialTerm")

class SettingsManager:
    """
    Gestionnaire des paramètres de l'application CrazySerialTerm.
    Permet de sauvegarder, charger, réinitialiser les paramètres utilisateur via QSettings.
    """
    
    def __init__(self, app_name: str = "SerialTerminal", settings_name: str = "Settings") -> None:
        """
        Initialise le gestionnaire de paramètres.
        Args:
            app_name (str): Nom de l'application.
            settings_name (str): Nom du groupe de paramètres.
        """
        self.settings: QSettings = QSettings(app_name, settings_name)
    
    def save_setting(self, key: str, value: Any) -> None:
        """
        Sauvegarde une valeur de paramètre.
        Args:
            key (str): Clé du paramètre.
            value (Any): Valeur à sauvegarder.
        """
        try:
            self.settings.setValue(key, value)
            self.settings.sync()
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du paramètre {key}: {e}")
            raise
    
    def load_setting(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Charge une valeur de paramètre.
        Args:
            key (str): Clé du paramètre.
            default (Any, optionnel): Valeur par défaut si le paramètre n'existe pas.
        Returns:
            Any: Valeur du paramètre ou valeur par défaut.
        """
        try:
            value: Any = self.settings.value(key, default)
            return value
        except Exception as e:
            logger.error(f"Erreur lors du chargement du paramètre {key}: {str(e)}")
            return default
    
    def save_all_settings(self, settings_dict: Dict[str, Any]) -> None:
        """
        Sauvegarde un dictionnaire complet de paramètres.
        Args:
            settings_dict (Dict[str, Any]): Dictionnaire des paramètres à sauvegarder.
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
            Dict[str, Any]: Dictionnaire des paramètres chargés.
        """
        settings_dict: Dict[str, Any] = {}
        try:
            for key in self.settings.allKeys():
                settings_dict[key] = self.settings.value(key)
            logger.info("Tous les paramètres chargés")
            return settings_dict
        except Exception as e:
            logger.error(f"Erreur lors du chargement des paramètres: {str(e)}")
            return {}
    
    def reset_to_defaults(self) -> None:
        """
        Remet tous les paramètres à leur valeur par défaut.
        """
        try:
            self.settings.clear()
            self.settings.sync()
            logger.info("Paramètres remis à zéro")
        except Exception as e:
            logger.error(f"Erreur lors de la remise à zéro: {str(e)}")

__all__ = []
