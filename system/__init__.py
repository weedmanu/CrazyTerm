"""
System Package pour CrazyTerm.

Ce package contient les composants système de l'application CrazyTerm,
incluant la gestion d'erreurs, l'optimisation mémoire et les utilitaires.

Modules:
    - error_handling: Gestion d'erreurs robuste
    - memory_optimizer: Optimisation mémoire
    - custom_exceptions: Exceptions personnalisées
    - utilities: Utilitaires système

Fonctionnalités:
    - Gestion d'erreurs centralisée
    - Optimisation mémoire intelligente
    - Système d'exceptions personnalisées
    - Utilitaires système et performance
    - Monitoring et métriques
    - Logging avancé

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
    from .error_handling import ErrorHandler
    from .memory_optimizer import MemoryOptimizer
    from .custom_exceptions import *
    from .utilities import Utilities
    
    # Liste des exports publics
    __all__ = [
        'ErrorHandler',
        'MemoryOptimizer',
        'Utilities',
        'logger',
        '__version__',
        '__author__',
        '__email__',
        '__license__'
    ]
    
    # Validation et robustesse
    assert len(__all__) >= 4, "Package système doit avoir au moins 4 modules"
    
    logger.info(f"System package v{__version__} chargé avec succès")
    
except ImportError as e:
    logger.warning(f"Impossible d'importer certains modules système: {e}")
    __all__ = ['logger', '__version__', '__author__', '__email__', '__license__']
    raise ImportError(f"Erreur critique lors du chargement du package système: {e}")
except AssertionError as e:
    logger.error(f"Validation du package système échouée: {e}")
    raise
except Exception as e:
    logger.error(f"Erreur inattendue dans le package système: {e}")
    raise


def get_version() -> str:
    """
    Retourne la version du package system.
    
    Returns:
        str: Version du package
        
    Examples:
        >>> from system import get_version
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
        >>> from system import get_package_info
        >>> info = get_package_info()
        >>> print(info['version'])
        1.0.0
    """
    return {
        'name': 'system',
        'version': __version__,
        'author': __author__,
        'email': __email__,
        'license': __license__,
        'description': 'Package système pour CrazyTerm'
    }


def configure_logging(level: str = 'INFO') -> None:
    """
    Configure le logging pour le package system.
    
    Args:
        level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Examples:
        >>> from system import configure_logging
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


def get_system_health() -> Dict[str, Any]:
    """Retourne l'état de santé du package système."""
    try:
        with _create_system_context():
            return {
                'package_name': 'system',
                'version': __version__,
                'modules_loaded': len(__all__),
                'logger_active': hasattr(logger, 'info'),
                'critical_modules': ['ErrorHandler', 'MemoryOptimizer']
            }
    except Exception as e:
        logger.error(f"Erreur santé système: {e}")
        return {'error': str(e)}


def _create_system_context():
    """Contexte pour vérification système."""
    from contextlib import contextmanager
    
    @contextmanager
    def context():
        logger.debug("Vérification santé système")
        try:
            yield
        finally:
            logger.debug("Fin vérification système")
    
    return context()


class SystemManager:
    """
    Gestionnaire central du système pour CrazyTerm.
    
    Cette classe coordonne les utilitaires système, la gestion d'erreurs
    et l'optimisation mémoire.
    
    Attributes:
        _services (Dict[str, Any]): Services système
        _memory_optimizer (Any): Optimiseur mémoire
        
    Methods:
        __init__: Initialise le gestionnaire
        start_service: Démarre un service
        stop_service: Arrête un service
        optimize_memory: Lance l'optimisation mémoire
        
    Examples:
        >>> manager = SystemManager()
        >>> manager.optimize_memory()
        
    Note:
        Cette classe centralise la gestion du système.
    """
    
    def __init__(self) -> None:
        """Initialise le gestionnaire système."""
        self._services = {}
        self._memory_optimizer = None
        self.logger = logger
        self.logger.info("SystemManager initialisé")
    
    def start_service(self, service_name: str, service: Any) -> bool:
        """
        Démarre un service système.
        
        Args:
            service_name: Nom du service
            service: Instance du service
            
        Returns:
            bool: True si le service a été démarré
        """
        try:
            self._services[service_name] = service
            if hasattr(service, 'start'):
                service.start()
            self.logger.info(f"Service '{service_name}' démarré")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors du démarrage du service '{service_name}': {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Arrête un service système."""
        try:
            if service_name in self._services:
                service = self._services[service_name]
                if hasattr(service, 'stop'):
                    service.stop()
                del self._services[service_name]
                self.logger.info(f"Service '{service_name}' arrêté")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de l'arrêt du service '{service_name}': {e}")
            return False
    
    def optimize_memory(self) -> bool:
        """Lance l'optimisation mémoire."""
        try:
            if self._memory_optimizer:
                self._memory_optimizer.optimize()
            self.logger.info("Optimisation mémoire effectuée")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'optimisation mémoire: {e}")
            return False
    
    def __str__(self) -> str:
        """Représentation string du gestionnaire."""
        return f"SystemManager(services={len(self._services)})"
    
    def __repr__(self) -> str:
        """Représentation détaillée du gestionnaire."""
        return f"SystemManager(_services={list(self._services.keys())})"


# Ajouter la classe aux exports
__all__.append('SystemManager')
