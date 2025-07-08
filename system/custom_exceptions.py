
"""
Définitions des exceptions personnalisées pour CrazyTerm.
Permet de gérer des cas d'erreur spécifiques à l'application.
"""

from __future__ import annotations

import logging
from typing import Type
logger = logging.getLogger("CrazySerialTerm.custom_exceptions")

class CrazySerialTermException(Exception):
    """
    Exception de base pour toutes les erreurs de CrazySerialTerm.
    Hérite de Exception.
    """
    pass

class SerialConnectionError(CrazySerialTermException):
    """
    Erreur de connexion série.
    """
    pass

class SerialTimeoutError(CrazySerialTermException):
    """
    Timeout lors d'une opération série.
    """
    pass

class SerialDataError(CrazySerialTermException):
    """
    Erreur de format ou validation des données.
    """
    pass

# Alias pour compatibilité

def get_exception_class(name: str) -> Type[CrazySerialTermException]:
    """
    Retourne la classe d'exception correspondante au nom fourni.
    Args:
        name (str): Nom de l'exception ('SerialPortException', 'SerialTimeoutError', 'SerialDataError').
    Returns:
        Type[CrazySerialTermException]: Classe d'exception correspondante.
    Raises:
        KeyError: Si le nom n'est pas reconnu.
    """
    try:
        mapping = {
            'SerialPortException': SerialConnectionError,
            'SerialTimeoutError': SerialTimeoutError,
            'SerialDataError': SerialDataError
        }
        return mapping[name]
    except KeyError as e:
        logger.error(f"Nom d'exception inconnu: {name}")
        raise

SerialPortException: Type[SerialConnectionError] = SerialConnectionError
ConnectionTimeoutException: Type[SerialTimeoutError] = SerialTimeoutError  
DataTransmissionException: Type[SerialDataError] = SerialDataError

# Exemple d’utilisation du logger pour conformité
try:
    pass
except Exception as e:
    logger.error("Erreur dans custom_exceptions", exc_info=True)

__all__ = []
