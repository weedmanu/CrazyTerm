"""
Utilitaires pour la robustesse et la gestion d'erreurs
"""

import time
import logging
import functools
from typing import Any, Callable, Type, Union, Tuple
from system.custom_exceptions import CrazySerialTermException

logger = logging.getLogger("CrazySerialTerm.Robustness")

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 0.1,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception
):
    """
    Décorateur pour retry automatique avec exponential backoff.
    
    Args:
        max_retries: Nombre maximum de tentatives
        initial_delay: Délai initial en secondes
        backoff_factor: Facteur multiplicateur pour le délai
        max_delay: Délai maximum en secondes
        exceptions: Type(s) d'exception à capturer pour retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"Échec définitif de {func.__name__} après {max_retries} tentatives: {e}")
                        raise
                    
                    logger.warning(f"Tentative {attempt + 1}/{max_retries + 1} échouée pour {func.__name__}: {e}")
                    time.sleep(min(delay, max_delay))
                    delay *= backoff_factor
                    
            # Ne devrait jamais arriver, mais par sécurité
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator

def safe_execute(func: Callable, default_value: Any = None, log_errors: bool = True) -> Any:
    """
    Exécute une fonction de manière sécurisée avec gestion d'erreur.
    
    Args:
        func: Fonction à exécuter
        default_value: Valeur par défaut en cas d'erreur
        log_errors: Si True, log les erreurs
        
    Returns:
        Résultat de la fonction ou default_value en cas d'erreur
    """
    try:
        return func()
    except Exception as e:
        if log_errors:
            logger.error(f"Erreur lors de l'exécution de {func.__name__}: {e}")
        return default_value

class CircuitBreaker:
    """
    Implémentation du pattern Circuit Breaker pour éviter les appels répétés 
    à des services défaillants.
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Exécute une fonction à travers le circuit breaker.
        """
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise CrazySerialTermException("Circuit breaker is OPEN")
                
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
            
    def _should_attempt_reset(self) -> bool:
        """Vérifie si on peut tenter une remise à zéro."""
        return (self.last_failure_time and 
                time.time() - self.last_failure_time >= self.recovery_timeout)
                
    def _on_success(self):
        """Appelé en cas de succès."""
        self.failure_count = 0
        self.state = 'CLOSED'
        
    def _on_failure(self):
        """Appelé en cas d'échec."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"Circuit breaker ouvert après {self.failure_count} échecs")

class ResourceGuard:
    """
    Context manager pour la gestion robuste des ressources.
    """
    
    def __init__(self, resource, cleanup_func: Callable = None):
        self.resource = resource
        self.cleanup_func = cleanup_func
        
    def __enter__(self):
        return self.resource
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cleanup_func:
            safe_execute(self.cleanup_func, log_errors=True)
        elif hasattr(self.resource, 'close'):
            safe_execute(self.resource.close, log_errors=True)
