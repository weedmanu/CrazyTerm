"""Config Manager Module pour CrazyTerm."""

import logging
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigManager:
    """Gestionnaire de configuration pour CrazyTerm."""
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None) -> None:
        """Initialise le gestionnaire de configuration."""
        self._config_file = Path(config_file) if config_file else Path("config.json")
        self._config_data: Dict[str, Any] = {}
        self._default_config: Dict[str, Any] = {
            "theme": "dark",
            "font_size": 12,
            "font_family": "Consolas",
            "serial_settings": {
                "baudrate": 9600,
                "timeout": 1.0,
                "bytesize": 8,
                "parity": "N",
                "stopbits": 1
            },
            "window_settings": {
                "width": 800,
                "height": 600,
                "maximized": False
            },
            "auto_save": True,
            "logging_level": "INFO"
        }
        
        logger.info(f"ConfigManager initialisé avec le fichier: {self._config_file}")
        self._load_config()
    
    def _load_config(self) -> None:
        """Charge la configuration depuis le fichier."""
        try:
            if self._config_file.exists():
                with open(self._config_file, "r", encoding="utf-8") as f:
                    self._config_data = json.load(f)
                logger.info("Configuration chargée avec succès")
            else:
                self._config_data = self._default_config.copy()
                logger.info("Configuration par défaut utilisée")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            self._config_data = self._default_config.copy()
    
    def save_config(self) -> bool:
        """Sauvegarde la configuration dans le fichier."""
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(self._config_data, f, indent=2, ensure_ascii=False)
            
            logger.info("Configuration sauvegardée avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration."""
        try:
            keys = key.split(".")
            value = self._config_data
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
                    
            return value
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la clé {key}: {e}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Définit une valeur de configuration."""
        try:
            keys = key.split(".")
            config = self._config_data
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
            
            logger.debug(f"Configuration mise à jour: {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la définition de la clé {key}: {e}")
            return False
    
    def reset_to_default(self) -> None:
        """Remet la configuration aux valeurs par défaut."""
        self._config_data = self._default_config.copy()
        logger.info("Configuration remise aux valeurs par défaut")
    
    def get_all(self) -> Dict[str, Any]:
        """Retourne toute la configuration."""
        return self._config_data.copy()
    
    def __str__(self) -> str:
        """Retourne une représentation string de la configuration."""
        return f"ConfigManager(file={self._config_file}, keys={len(self._config_data)})"


# Configuration globale pour le module
_global_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Retourne l'instance globale de ConfigManager."""
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager()
    return _global_config


logger.info("Module config_manager initialisé")
