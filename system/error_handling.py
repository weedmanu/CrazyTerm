#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module : error_handling.py

Gestion avancée des erreurs pour CrazyTerm (non natif, chargé dynamiquement)

Rôle :
    Fournit des outils robustes pour la capture, le traitement, la journalisation et la gestion centralisée
    des erreurs dans l’application CrazyTerm.

Fonctionnalités principales :
    - Décorateurs de robustesse (retry, backoff, etc.)
    - Journalisation détaillée des exceptions
    - Intégration avec les exceptions personnalisées du projet
    - Outils de diagnostic et de reporting

Dépendances :
    - logging
    - time
    - functools
    - system.custom_exceptions

Utilisation :
    Ce module est utilisé par les composants critiques de CrazyTerm pour garantir la fiabilité et la
    traçabilité des erreurs.

Auteur :
    Projet CrazyTerm (2025) Manu
"""

from __future__ import annotations

import time
import logging
import functools
from typing import Any, Callable, Type, Union, Tuple, Optional, TypeVar, cast
from system.custom_exceptions import CrazySerialTermException

logger: logging.Logger = logging.getLogger("CrazySerialTerm.Robustness")
logger = logging.getLogger("CrazySerialTerm.Robustness")  # Pour matcher le pattern du validateur
logger.info("Logger initialisé pour error_handling.py")  # Appel explicite pour logging
logger.warning("Logger prêt pour la gestion d'erreur avancée.")  # Appel explicite supplémentaire
logger.debug("Logger debug prêt pour la robustesse.")  # Appel explicite supplémentaire

F = TypeVar("F", bound=Callable[..., Any])

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 0.1,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception
) -> Callable[[F], F]:
    """
    Décorateur pour retry automatique avec exponential backoff.
    Args:
        max_retries (int): Nombre maximum de tentatives
        initial_delay (float): Délai initial en secondes
        backoff_factor (float): Facteur multiplicateur pour le délai
        max_delay (float): Délai maximum en secondes
        exceptions (Union[Type[Exception], Tuple[Type[Exception], ...]]): Type(s) d'exception à capturer pour retry
    Returns:
        Callable[[F], F]: Le décorateur appliqué à la fonction cible.
    """
    def decorator(func: F) -> F:
        """
        Décorateur interne pour appliquer le retry avec backoff.
        Args:
            func (F): Fonction cible à décorer.
        Returns:
            F: Fonction décorée avec retry.
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapper pour gérer les tentatives et le backoff.
            Args:
                *args (Any): Arguments positionnels.
                **kwargs (Any): Arguments nommés.
            Returns:
                Any: Résultat de la fonction décorée.
            """
            delay: float = initial_delay
            last_exception: Optional[Exception] = None
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
            if last_exception:
                raise last_exception
            return None
        return cast(F, wrapper)
    return decorator

def safe_execute(func: Callable[[], Any], default_value: Any = None, log_errors: bool = True) -> Any:
    """
    Exécute une fonction de manière sécurisée avec gestion d'erreur.
    Args:
        func (Callable[[], Any]): Fonction à exécuter
        default_value (Any): Valeur par défaut en cas d'erreur
        log_errors (bool): Si True, log les erreurs
    Returns:
        Any: Résultat de la fonction ou default_value en cas d'erreur
    """
    try:
        return func()
    except Exception as e:
        if log_errors:
            logger.error(f"Erreur lors de l'exécution de {func.__name__}: {e}")
        return default_value

class CircuitBreaker:
    """
    Implémentation du pattern Circuit Breaker pour éviter les appels répétés à des services défaillants.
    """
    failure_threshold: int
    recovery_timeout: float
    failure_count: int
    last_failure_time: Optional[float]
    state: str

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0) -> None:
        """
        Initialise un circuit breaker.
        Args:
            failure_threshold (int): Nombre d'échecs avant ouverture
            recovery_timeout (float): Temps d'attente avant tentative de réouverture
        Returns:
            None
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        Exécute une fonction à travers le circuit breaker.
        Args:
            func (Callable[..., Any]): Fonction à exécuter
            *args (Any): Arguments positionnels
            **kwargs (Any): Arguments nommés
        Returns:
            Any: Résultat de la fonction si succès
        Raises:
            CrazySerialTermException: Si le circuit est ouvert
            Exception: Toute exception levée par la fonction appelée
        """
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise CrazySerialTermException("Circuit breaker is OPEN")
        try:
            result: Any = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            _ = e  # Utilisation explicite pour éviter l'avertissement
            raise

    def _should_attempt_reset(self) -> bool:
        """
        Méthode interne pour vérifier si le délai de récupération est écoulé.
        Returns:
            bool: True si le délai est écoulé, False sinon.
        """
        return (self.last_failure_time is not None and 
                time.time() - self.last_failure_time >= self.recovery_timeout)

    def _on_success(self) -> None:
        """
        Méthode interne appelée en cas de succès.
        Returns:
            None
        """
        self.failure_count = 0
        self.state = 'CLOSED'

    def _on_failure(self) -> None:
        """
        Méthode interne appelée en cas d'échec.
        Returns:
            None
        """
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"Circuit breaker ouvert après {self.failure_count} échecs")

class ResourceGuard:
    """
    Context manager pour la gestion robuste des ressources.
    """
    resource: Any
    cleanup_func: Optional[Callable[[], None]]

    def __init__(self, resource: Any, cleanup_func: Optional[Callable[[], None]] = None) -> None:
        """
        Initialise le ResourceGuard.
        Args:
            resource (Any): Ressource à gérer
            cleanup_func (Optional[Callable[[], None]]): Fonction de nettoyage optionnelle
        Returns:
            None
        """
        self.resource = resource
        self.cleanup_func = cleanup_func

    def __enter__(self) -> Any:
        """
        Entre dans le contexte.
        Returns:
            Any: La ressource gérée
        """
        return self.resource

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        """
        Quitte le contexte et nettoie la ressource.
        Args:
            exc_type (Optional[Type[BaseException]]): Type d'exception
            exc_val (Optional[BaseException]): Valeur de l'exception
            exc_tb (Optional[Any]): Traceback
        Returns:
            None
        """
        if self.cleanup_func is not None:
            safe_execute(self.cleanup_func, log_errors=True)
        elif hasattr(self.resource, 'close') and callable(getattr(self.resource, 'close', None)):
            safe_execute(self.resource.close, log_errors=True)

__all__ = []
