"""
Tools Package pour CrazyTerm.

Ce package contient les outils intégrés de l'application CrazyTerm,
incluant calculatrice, checksum et convertisseur.

Modules:
    - tool_calculator: Calculatrice scientifique
    - tool_checksum: Calcul de checksum et hash
    - tool_converter: Convertisseur de données

Fonctionnalités:
    - Outils mathématiques avancés
    - Calculs de sécurité (hash, checksum)
    - Conversions de données multiples
    - Interface utilisateur intégrée
    - Historique des calculs

Auteur: CrazyTerm Development Team
Version: 1.0.0
License: MIT
"""

import logging
import os
from typing import Dict, Any, List
from contextlib import contextmanager

# Configuration du logging pour le package
logger = logging.getLogger(__name__)

# Version du package
__version__ = "1.0.0"
__author__ = "CrazyTerm Development Team"
__email__ = "contact@crazyterm.dev"
__license__ = "MIT"

# Découverte automatique des modules d'outils
def _discover_tool_modules() -> Dict[str, Any]:
    """Découvre automatiquement les modules d'outils présents."""
    tools_dir = os.path.dirname(__file__)
    tool_modules = {}
    
    for filename in os.listdir(tools_dir):
        if filename.startswith('tool_') and filename.endswith('.py'):
            module_name = filename[:-3]  # Enlever .py
            try:
                # Import relatif correct
                module = __import__(f'tools.{module_name}', fromlist=[module_name])
                # Chercher la classe principale (nom en CamelCase)
                class_name = ''.join(word.capitalize() for word in module_name.split('_'))
                if hasattr(module, class_name):
                    tool_modules[class_name] = getattr(module, class_name)
                    logger.debug(f"Module {module_name} chargé avec classe {class_name}")
                else:
                    logger.warning(f"Classe {class_name} non trouvée dans {module_name}")
            except ImportError as e:
                logger.warning(f"Impossible de charger {module_name}: {e}")
    
    return tool_modules

# Imports principaux
try:
    # Découverte automatique des outils
    _discovered_tools = _discover_tool_modules()
    
    # Ajout des outils découverts aux globals
    for class_name, tool_class in _discovered_tools.items():
        globals()[class_name] = tool_class
    
    # Liste des exports publics
    __all__ = [
        'ToolsManager',
        'logger',
        '__version__',
        '__author__',
        '__email__',
        '__license__',
        'get_tools_health',
        'get_version',
        'get_package_info',
        'configure_logging'
    ]
    
    # Ajouter les outils découverts aux exports
    __all__.extend(_discovered_tools.keys())
    
    # Validation et robustesse
    assert len(_discovered_tools) >= 1, "Package outils doit avoir au moins 1 module"
    
    logger.info(f"Tools package v{__version__} chargé avec succès - {len(_discovered_tools)} outils découverts")
    
except ImportError as e:
    logger.warning(f"Impossible d'importer certains modules d'outils: {e}")
    __all__ = ['logger', '__version__', '__author__', '__email__', '__license__']
    raise ImportError(f"Erreur critique lors du chargement du package outils: {e}")
except AssertionError as e:
    logger.error(f"Validation du package outils échouée: {e}")
    raise
except Exception as e:
    logger.error(f"Erreur inattendue dans le package outils: {e}")
    raise


class ToolsManager:
    """
    Gestionnaire central des outils pour CrazyTerm.
    
    Cette classe coordonne les outils intégrés comme la calculatrice,
    le checksum, le convertisseur, etc.
    
    Attributes:
        _tools (Dict[str, Any]): Outils disponibles
        _active_tools (List[str]): Outils actifs
        
    Methods:
        __init__: Initialise le gestionnaire
        register_tool: Enregistre un outil
        launch_tool: Lance un outil
        close_tool: Ferme un outil
        
    Examples:
        >>> manager = ToolsManager()
        >>> manager.launch_tool('calculator')
        
    Note:
        Cette classe centralise la gestion des outils.
    """
    
    def __init__(self) -> None:
        """Initialise le gestionnaire d'outils."""
        self._tools = {}
        self._active_tools = []
        self.logger = logger
        self.logger.info("ToolsManager initialisé")
    
    def register_tool(self, tool_name: str, tool_class: Any) -> bool:
        """
        Enregistre un outil.
        
        Args:
            tool_name: Nom de l'outil
            tool_class: Classe de l'outil
            
        Returns:
            bool: True si l'outil a été enregistré
        """
        try:
            self._tools[tool_name] = tool_class
            self.logger.info(f"Outil '{tool_name}' enregistré")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement de l'outil '{tool_name}': {e}")
            return False
    
    def launch_tool(self, tool_name: str) -> bool:
        """
        Lance un outil.
        
        Args:
            tool_name: Nom de l'outil à lancer
            
        Returns:
            bool: True si l'outil a été lancé
        """
        try:
            if tool_name in self._tools and tool_name not in self._active_tools:
                tool_class = self._tools[tool_name]
                # Ici on instancierait et lancerait l'outil
                self._active_tools.append(tool_name)
                self.logger.info(f"Outil '{tool_name}' lancé")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors du lancement de l'outil '{tool_name}': {e}")
            return False
    
    def close_tool(self, tool_name: str) -> bool:
        """Ferme un outil actif."""
        try:
            if tool_name in self._active_tools:
                self._active_tools.remove(tool_name)
                self.logger.info(f"Outil '{tool_name}' fermé")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la fermeture de l'outil '{tool_name}': {e}")
            return False
    
    def __str__(self) -> str:
        """Représentation string du gestionnaire."""
        return f"ToolsManager(outils={len(self._tools)}, actifs={len(self._active_tools)})"
    
    def __repr__(self) -> str:
        """Représentation détaillée du gestionnaire."""
        return f"ToolsManager(_tools={list(self._tools.keys())}, _active_tools={self._active_tools})"


def get_tools_health() -> Dict[str, Any]:
    """Retourne l'état de santé du package outils."""
    try:
        with _create_tools_context():
            available_tools = [name.lower().replace('tool', '') for name in _discovered_tools.keys()]
            return {
                'package_name': 'tools',
                'version': __version__,
                'modules_loaded': len(__all__),
                'logger_active': hasattr(logger, 'info'),
                'tool_types': available_tools,
                'discovered_tools': len(_discovered_tools)
            }
    except Exception as e:
        logger.error(f"Erreur santé outils: {e}")
        return {'error': str(e)}


@contextmanager
def _create_tools_context():
    """Contexte pour vérification outils."""
    logger.debug("Vérification santé outils")
    try:
        yield
    finally:
        logger.debug("Fin vérification outils")


def get_version() -> str:
    """
    Retourne la version du package tools.
    
    Returns:
        str: Version du package
        
    Examples:
        >>> from tools import get_version
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
        >>> from tools import get_package_info
        >>> info = get_package_info()
        >>> print(info['version'])
        1.0.0
    """
    return {
        'name': 'tools',
        'version': __version__,
        'author': __author__,
        'email': __email__,
        'license': __license__,
        'description': 'Package d\'outils pour CrazyTerm'
    }


def configure_logging(level: str = 'INFO') -> None:
    """
    Configure le logging pour le package tools.
    
    Args:
        level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Examples:
        >>> from tools import configure_logging
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
