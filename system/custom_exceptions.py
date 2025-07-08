"""
Exceptions personnalisées pour CrazySerialTerm
Hiérarchie d'exceptions pour une gestion d'erreur robuste.
"""

class CrazySerialTermException(Exception):
    """Exception de base pour toutes les erreurs de CrazySerialTerm."""
    pass

class SerialConnectionError(CrazySerialTermException):
    """Erreur de connexion série."""
    pass

class SerialTimeoutError(CrazySerialTermException):
    """Timeout lors d'une opération série."""
    pass

class SerialDataError(CrazySerialTermException):
    """Erreur de format ou validation des données."""
    pass
