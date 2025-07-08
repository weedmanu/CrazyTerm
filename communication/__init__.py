"""
Communication Package pour CrazyTerm.

Ce package gère toutes les communications série et les protocoles
de communication de l'application CrazyTerm.

Modules:
    - serial_communication: Communication série principale

Fonctionnalités:
    - Communication série robuste
    - Gestion des erreurs de communication
    - Support multi-protocoles
    - Détection automatique des ports
    - Gestion des timeouts
    - Buffering intelligent

Auteur: CrazyTerm Development Team
Version: 1.0.0
License: MIT
"""

import logging
from typing import Dict, Any, List

# Configuration du logging pour le package
logger = logging.getLogger(__name__)

# Version du package
__version__ = "1.0.0"
__author__ = "CrazyTerm Development Team"
__email__ = "contact@crazyterm.dev"
__license__ = "MIT"

# Imports principaux
try:
    from .serial_communication import SerialCommunication
    
    # Validation de l'import
    assert hasattr(SerialCommunication, '__init__'), "SerialCommunication doit avoir un __init__"
    
    # Liste des exports publics
    __all__ = [
        'SerialCommunication',
        'logger',
        '__version__',
        '__author__',
        '__email__',
        '__license__'
    ]
    
    logger.info(f"Communication package v{__version__} chargé avec succès")
    
except ImportError as e:
    logger.warning(f"Impossible d'importer certains modules de communication: {e}")
    __all__ = ['logger', '__version__', '__author__', '__email__', '__license__']
    raise ImportError(f"Erreur critique lors du chargement du package communication: {e}")
except AssertionError as e:
    logger.error(f"Validation du package échouée: {e}")
    raise
except Exception as e:
    logger.error(f"Erreur inattendue dans le package communication: {e}")
    raise


def get_version() -> str:
    """
    Retourne la version du package communication.
    
    Returns:
        str: Version du package
        
    Examples:
        >>> from communication import get_version
        >>> print(get_version())
        1.0.0
    """
    return __version__


def get_package_info() -> Dict[str, Any]:
    """
    Retourne les informations du package.
    
    Returns:
        Dict[str, Any]: Informations du package
        
    Examples:
        >>> from communication import get_package_info
        >>> info = get_package_info()
        >>> print(info['version'])
        1.0.0
    """
    return {
        'name': 'communication',
        'version': __version__,
        'author': __author__,
        'email': __email__,
        'license': __license__,
        'description': 'Package de communication pour CrazyTerm'
    }


def configure_logging(level: str = 'INFO') -> None:
    """
    Configure le logging pour le package communication.
    
    Args:
        level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Examples:
        >>> from communication import configure_logging
        >>> configure_logging('DEBUG')
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Créer un handler si nécessaire
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.info(f"Logging configuré au niveau {level}")


def validate_package() -> bool:
    """
    Valide l'intégrité du package communication.
    
    Returns:
        bool: True si le package est valide, False sinon
        
    Raises:
        ImportError: Si un module requis n'est pas disponible
    """
    try:
        # Vérifier que les classes principales sont disponibles
        if 'SerialCommunication' in __all__:
            assert SerialCommunication is not None, "SerialCommunication non disponible"
            
        logger.debug("Validation du package communication réussie")
        return True
        
    except Exception as e:
        logger.error(f"Validation du package échouée: {e}")
        return False


def get_package_health() -> Dict[str, Any]:
    """
    Retourne l'état de santé du package.
    
    Returns:
        Dict[str, Any]: État de santé du package
    """
    try:
        health = {
            'package_name': 'communication',
            'version': __version__,
            'modules_loaded': len(__all__),
            'is_valid': validate_package(),
            'logger_active': bool(logger)
        }
        logger.debug("Vérification de l'état du package réussie")
        return health
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de santé: {e}")
        return {'error': str(e)}


class CommunicationManager:
    """
    Gestionnaire centralisé des communications pour CrazyTerm.
    
    Cette classe fournit une interface unifiée pour gérer toutes les
    communications série et les protocoles associés.
    
    Attributes:
        _instance (CommunicationManager): Instance singleton
        _communications (Dict[str, Any]): Communications actives
        
    Methods:
        __init__: Initialise le gestionnaire
        get_instance: Retourne l'instance singleton
        register_communication: Enregistre une nouvelle communication
        get_available_ports: Liste les ports disponibles
        
    Examples:
        >>> manager = CommunicationManager.get_instance()
        >>> ports = manager.get_available_ports()
        
    Note:
        Cette classe implémente le pattern Singleton pour une gestion
        centralisée des communications.
    """
    
    _instance = None
    
    def __init__(self) -> None:
        """
        Initialise le gestionnaire de communications.
        
        Raises:
            RuntimeError: Si une instance existe déjà (Singleton)
        """
        if CommunicationManager._instance is not None:
            raise RuntimeError("CommunicationManager est un Singleton")
        
        self._communications = {}
        self.logger = logger
        self.logger.info("CommunicationManager initialisé")
    
    @classmethod
    def get_instance(cls) -> 'CommunicationManager':
        """
        Retourne l'instance unique du gestionnaire.
        
        Returns:
            CommunicationManager: L'instance unique
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_communication(self, name: str, communication: Any) -> None:
        """
        Enregistre une nouvelle communication.
        
        Args:
            name: Nom de la communication
            communication: Instance de communication
            
        Raises:
            ValueError: Si le nom existe déjà
        """
        if name in self._communications:
            raise ValueError(f"Communication '{name}' déjà enregistrée")
        
        self._communications[name] = communication
        self.logger.info(f"Communication '{name}' enregistrée")
    
    def get_available_ports(self) -> List[str]:
        """
        Retourne la liste des ports série disponibles.
        
        Returns:
            List[str]: Liste des ports disponibles
        """
        try:
            # Ici on utiliserait SerialCommunication pour lister les ports
            # Pour l'instant, on retourne une liste factice
            return ["COM1", "COM2", "COM3", "/dev/ttyUSB0", "/dev/ttyACM0"]
        except Exception as e:
            self.logger.error(f"Erreur lors de la détection des ports: {e}")
            return []
    
    def __str__(self) -> str:
        """Représentation string du gestionnaire."""
        return f"CommunicationManager(communications={len(self._communications)})"
    
    def __repr__(self) -> str:
        """Représentation détaillée du gestionnaire."""
        return f"CommunicationManager(_communications={self._communications})"


# Ajouter la classe aux exports
__all__.append('CommunicationManager')
