"""
Module de gestion des paramètres et de la configuration pour CrazySerialTerm.
Ce module fournit un gestionnaire professionnel pour la sauvegarde, le chargement et la réinitialisation
 des paramètres de l'application, avec gestion d'erreur robuste et journalisation.
Toutes les méthodes sont documentées et typées selon les standards professionnels.
"""

from __future__ import annotations

from typing import Dict, Any, Optional
import logging
import os
from system.utilities import UtilityFunctions
import json

logger = logging.getLogger("CrazySerialTerm")

class SettingsManager:
    """
    Gestionnaire des paramètres de l'application CrazySerialTerm.
    Permet de sauvegarder, charger, réinitialiser les paramètres utilisateur via un fichier JSON centralisé.
    """
    CONFIG_PATH = UtilityFunctions.resource_path('config/settings.json')

    @staticmethod
    def load_all_settings() -> Dict[str, Any]:
        """
        Charge tous les paramètres depuis le fichier JSON centralisé.
        Returns:
            Dict[str, Any]: Dictionnaire des paramètres chargés.
        """
        try:
            if not os.path.exists(SettingsManager.CONFIG_PATH):
                # Création automatique d'un fichier de config vide si absent
                with open(SettingsManager.CONFIG_PATH, 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=4, ensure_ascii=False)
                logger.warning(f"Fichier de configuration absent, créé vide : {SettingsManager.CONFIG_PATH}")
            return UtilityFunctions.load_app_settings()
        except json.JSONDecodeError as e:
            logger.error(f"Fichier de configuration JSON corrompu : {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors du chargement des paramètres: {e}")
            raise

    @staticmethod
    def save_all_settings(settings_dict: Dict[str, Any]) -> None:
        """
        Sauvegarde un dictionnaire complet de paramètres dans le fichier JSON centralisé.
        Args:
            settings_dict (Dict[str, Any]): Dictionnaire des paramètres à sauvegarder.
        """
        try:
            with open(SettingsManager.CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(settings_dict, f, indent=4, ensure_ascii=False)
            logger.info("Tous les paramètres sauvegardés dans le JSON centralisé")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des paramètres: {e}")
            raise

    @staticmethod
    def load_setting(key: str, default: Optional[Any] = None) -> Any:
        """
        Charge une valeur de paramètre depuis le JSON centralisé.
        Args:
            key (str): Clé du paramètre.
            default (Any, optionnel): Valeur par défaut si le paramètre n'existe pas.
        Returns:
            Any: Valeur du paramètre ou valeur par défaut.
        """
        settings = SettingsManager.load_all_settings()
        return settings.get(key, default)

    @staticmethod
    def save_setting(key: str, value: Any) -> None:
        """
        Sauvegarde une valeur de paramètre dans le JSON centralisé.
        Args:
            key (str): Clé du paramètre.
            value (Any): Valeur à sauvegarder.
        """
        settings = SettingsManager.load_all_settings()
        settings[key] = value
        SettingsManager.save_all_settings(settings)

    @staticmethod
    def reset_to_defaults(defaults: Optional[Dict[str, Any]] = None) -> None:
        """
        Remet tous les paramètres à leur valeur par défaut (optionnel: dictionnaire de defaults).
        """
        if defaults is None:
            defaults = {}
        SettingsManager.save_all_settings(defaults)
        logger.info("Paramètres remis à zéro (JSON centralisé)")

__all__ = []
