"""
Core Package pour CrazyTerm.

Ce package contient les composants principaux de l'application CrazyTerm,
incluant la fenêtre principale, la gestion de configuration, et les managers.

Modules:
    - main_window: Fenêtre principale de l'application
    - config_manager: Gestionnaire de configuration
    - ui_manager: Gestionnaire d'interface utilisateur
    - tool_manager: Gestionnaire d'outils
    - terminal_display: Affichage du terminal
    - terminal_display_manager: Gestionnaire d'affichage du terminal

Auteur: CrazyTerm Development Team
Version: 1.0.0
License: MIT
"""

import logging
from typing import Dict, List, Optional, Union, Any, Tuple, Set, Callable

# Configuration du logging pour le package
logger = logging.getLogger(__name__)

# Version du package
__version__ = "1.0.0"
__author__ = "CrazyTerm Development Team"
__email__ = "contact@crazyterm.dev"
__license__ = "MIT"

# Imports principaux pour faciliter l'utilisation
try:
    from .main_window import MainWindow, MainWindowConfig
    from .config_manager import ConfigManager
    from .ui_manager import UIManager
    from .tool_manager import ToolManager
    from .terminal_display import TerminalDisplay
    
    # Liste des exports publics
    __all__ = [
        'MainWindow',
        'MainWindowConfig', 
        'ConfigManager',
        'UIManager',
        'ToolManager',
        'TerminalDisplay',
        'logger',
        '__version__',
        '__author__',
        '__email__',
        '__license__'
    ]
    
    # Validation des imports critiques
    assert hasattr(MainWindow, '__init__'), "MainWindow doit avoir un __init__"
    assert hasattr(ConfigManager, '__init__'), "ConfigManager doit avoir un __init__"
    
    # Mise à jour des exports
    __all__.extend(['validate_core_package', 'get_core_health'])
    
    logger.info(f"Core package v{__version__} chargé avec succès")
    
except ImportError as e:
    logger.warning(f"Impossible d'importer certains modules du core: {e}")
    __all__ = ['logger', '__version__', '__author__', '__email__', '__license__']
    raise ImportError(f"Erreur critique lors du chargement du package core: {e}")
except AssertionError as e:
    logger.error(f"Validation du package core échouée: {e}")
    raise
except Exception as e:
    logger.error(f"Erreur inattendue dans le package core: {e}")
    raise


def get_version() -> str:
    """
    Retourne la version du package core.
    
    Returns:
        str: Version du package
        
    Examples:
        >>> from core import get_version
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
        >>> from core import get_package_info
        >>> info = get_package_info()
        >>> print(info['version'])
        1.0.0
    """
    return {
        'name': 'core',
        'version': __version__,
        'author': __author__,
        'email': __email__,
        'license': __license__,
        'description': 'Core package pour CrazyTerm'
    }


def configure_logging(level: str = 'INFO') -> None:
    """
    Configure le logging pour le package core.
    
    Args:
        level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Examples:
        >>> from core import configure_logging
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


def validate_core_package() -> bool:
    """
    Valide l'intégrité du package core.
    
    Returns:
        bool: True si le package est valide, False sinon
        
    Raises:
        ImportError: Si un module requis n'est pas disponible
    """
    try:
        # Vérifier que les classes principales sont disponibles
        required_classes = ['MainWindow', 'ConfigManager', 'UIManager']
        for class_name in required_classes:
            if class_name in __all__:
                assert class_name in globals(), f"{class_name} non disponible"
                
        logger.debug("Validation du package core réussie")
        return True
        
    except Exception as e:
        logger.error(f"Validation du package core échouée: {e}")
        return False


def get_core_health() -> Dict[str, Any]:
    """
    Retourne l'état de santé du package core.
    
    Returns:
        Dict[str, Any]: État de santé du package
    """
    try:
        from contextlib import contextmanager
        
        @contextmanager
        def _health_context():
            logger.debug("Début vérification santé package core")
            try:
                yield
            finally:
                logger.debug("Fin vérification santé package core")
        
        with _health_context():
            health = {
                'package_name': 'core',
                'version': __version__,
                'modules_loaded': len(__all__),
                'is_valid': validate_core_package(),
                'logger_active': logger is not None and hasattr(logger, 'info'),
                'critical_modules': ['MainWindow', 'ConfigManager']
            }
            return health
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de santé du core: {e}")
        return {'error': str(e)}


class CoreManager:
    """
    Gestionnaire central des composants core de CrazyTerm.
    
    Cette classe coordonne l'initialisation et la gestion des composants
    principaux de l'application.
    
    Attributes:
        _components (Dict[str, Any]): Composants enregistrés
        _initialized (bool): État d'initialisation
        
    Methods:
        __init__: Initialise le gestionnaire
        register_component: Enregistre un composant
        get_component: Récupère un composant
        initialize_all: Initialise tous les composants
        
    Examples:
        >>> manager = CoreManager()
        >>> manager.register_component('main_window', window)
        >>> window = manager.get_component('main_window')
        
    Note:
        Cette classe centralise la gestion des composants core.
    """
    
    def __init__(self) -> None:
        """
        Initialise le gestionnaire des composants core.
        """
        self._components = {}
        self._initialized = False
        self.logger = logger
        self.logger.info("CoreManager initialisé")
    
    def register_component(self, name: str, component: Any) -> None:
        """
        Enregistre un composant core.
        
        Args:
            name: Nom du composant
            component: Instance du composant
            
        Raises:
            ValueError: Si le nom existe déjà
        """
        if name in self._components:
            raise ValueError(f"Composant '{name}' déjà enregistré")
        
        self._components[name] = component
        self.logger.info(f"Composant '{name}' enregistré")
    
    def get_component(self, name: str) -> Any:
        """
        Récupère un composant par son nom.
        
        Args:
            name: Nom du composant
            
        Returns:
            Any: Instance du composant
            
        Raises:
            KeyError: Si le composant n'existe pas
        """
        if name not in self._components:
            raise KeyError(f"Composant '{name}' non trouvé")
        
        return self._components[name]
    
    def initialize_all(self) -> bool:
        """
        Initialise tous les composants enregistrés.
        
        Returns:
            bool: True si tous les composants sont initialisés
        """
        try:
            for name, component in self._components.items():
                if hasattr(component, 'initialize'):
                    component.initialize()
                    self.logger.debug(f"Composant '{name}' initialisé")
            
            self._initialized = True
            self.logger.info("Tous les composants core initialisés")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation: {e}")
            return False
    
    def __str__(self) -> str:
        """Représentation string du gestionnaire."""
        status = "initialisé" if self._initialized else "non initialisé"
        return f"CoreManager(composants={len(self._components)}, {status})"
    
    def __repr__(self) -> str:
        """Représentation détaillée du gestionnaire."""
        return f"CoreManager(_components={list(self._components.keys())}, _initialized={self._initialized})"


# Ajouter la classe aux exports
__all__.append('CoreManager')
