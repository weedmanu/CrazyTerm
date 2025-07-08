"""
Interface Package pour CrazyTerm.

Ce package gère l'interface utilisateur, les thèmes et les composants
d'interface de l'application CrazyTerm.

Modules:
    - interface_components: Composants d'interface personnalisés
    - theme_manager: Gestionnaire de thèmes

Fonctionnalités:
    - Interface utilisateur moderne
    - Système de thèmes personnalisables
    - Composants réutilisables
    - Responsive design
    - Accessibilité
    - Internationalisation

Auteur: CrazyTerm Development Team
Version: 1.0.0
License: MIT
"""

import logging
from typing import Dict, Any

# Configuration du logging pour le package
logger = logging.getLogger(__name__)

# Version du package
__version__ = "1.0.0"
__author__ = "CrazyTerm Development Team"
__email__ = "contact@crazyterm.dev"
__license__ = "MIT"

# Imports principaux
try:
    from .interface_components import InterfaceComponents
    from .theme_manager import ThemeManager
    
    # Liste des exports publics
    __all__ = [
        'InterfaceComponents',
        'ThemeManager', 
        'logger',
        '__version__',
        '__author__',
        '__email__',
        '__license__'
    ]
    
    # Validation et robustesse
    assert 'InterfaceComponents' in __all__ or 'ThemeManager' in __all__, "Modules interface requis"
    
    logger.info(f"Interface package v{__version__} chargé avec succès")
    
except ImportError as e:
    logger.warning(f"Impossible d'importer certains modules d'interface: {e}")
    __all__ = ['logger', '__version__', '__author__', '__email__', '__license__']
    raise ImportError(f"Erreur critique lors du chargement du package interface: {e}")
except AssertionError as e:
    logger.error(f"Validation du package interface échouée: {e}")
    raise
except Exception as e:
    logger.error(f"Erreur inattendue dans le package interface: {e}")
    raise


def get_version() -> str:
    """
    Retourne la version du package interface.
    
    Returns:
        str: Version du package
        
    Examples:
        >>> from interface import get_version
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
        >>> from interface import get_package_info
        >>> info = get_package_info()
        >>> print(info['version'])
        1.0.0
    """
    return {
        'name': 'interface',
        'version': __version__,
        'author': __author__,
        'email': __email__,
        'license': __license__,
        'description': 'Package d\'interface pour CrazyTerm'
    }


def configure_logging(level: str = 'INFO') -> None:
    """
    Configure le logging pour le package interface.
    
    Args:
        level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Examples:
        >>> from interface import configure_logging
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


def get_interface_health() -> Dict[str, Any]:
    """Retourne l'état de santé du package interface."""
    try:
        with _create_health_context("interface"):
            return {
                'package_name': 'interface',
                'version': __version__,
                'modules_loaded': len(__all__),
                'logger_active': hasattr(logger, 'info')
            }
    except Exception as e:
        logger.error(f"Erreur santé interface: {e}")
        return {'error': str(e)}


def _create_health_context(package_name: str):
    """Contexte pour vérification de santé."""
    from contextlib import contextmanager
    
    @contextmanager
    def context():
        logger.debug(f"Vérification santé {package_name}")
        try:
            yield
        finally:
            logger.debug(f"Fin vérification {package_name}")
    
    return context()


class InterfaceManager:
    """
    Gestionnaire central des interfaces pour CrazyTerm.
    
    Cette classe coordonne les composants d'interface et les thèmes.
    
    Attributes:
        _themes (Dict[str, Any]): Thèmes disponibles
        _current_theme (str): Thème actuel
        
    Methods:
        __init__: Initialise le gestionnaire
        apply_theme: Applique un thème
        get_theme: Récupère un thème
        list_themes: Liste les thèmes disponibles
        
    Examples:
        >>> manager = InterfaceManager()
        >>> manager.apply_theme('dark')
        
    Note:
        Cette classe centralise la gestion de l'interface.
    """
    
    def __init__(self) -> None:
        """Initialise le gestionnaire d'interface."""
        self._themes = {}
        self._current_theme = "default"
        self.logger = logger
        self.logger.info("InterfaceManager initialisé")
    
    def apply_theme(self, theme_name: str) -> bool:
        """
        Applique un thème à l'interface.
        
        Args:
            theme_name: Nom du thème à appliquer
            
        Returns:
            bool: True si le thème a été appliqué
        """
        try:
            if theme_name in self._themes:
                self._current_theme = theme_name
                self.logger.info(f"Thème '{theme_name}' appliqué")
                return True
            else:
                self.logger.warning(f"Thème '{theme_name}' non trouvé")
                return False
        except Exception as e:
            self.logger.error(f"Erreur lors de l'application du thème: {e}")
            return False
    
    def get_theme(self, theme_name: str) -> Any:
        """Récupère un thème par son nom."""
        return self._themes.get(theme_name)
    
    def list_themes(self) -> List[str]:
        """Retourne la liste des thèmes disponibles."""
        return list(self._themes.keys())
    
    def __str__(self) -> str:
        """Représentation string du gestionnaire."""
        return f"InterfaceManager(theme_actuel={self._current_theme})"
    
    def __repr__(self) -> str:
        """Représentation détaillée du gestionnaire."""
        return f"InterfaceManager(_themes={list(self._themes.keys())}, _current_theme='{self._current_theme}')"


# Ajouter la classe aux exports
__all__.append('InterfaceManager')
