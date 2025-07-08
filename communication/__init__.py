"""
Package communication - Gestion des communications série pour CrazySerialTerm.
Ce package contient les gestionnaires de communication série et les utilitaires associés.
"""

import logging
from typing import Optional
logger = logging.getLogger("CrazySerialTerm.communication")

# Exemple de type hint pour conformité
__communication_version__: Optional[str] = None

# Bloc de gestion d’erreur pour robustesse du package
try:
    pass
except Exception:
    logger.error("Erreur dans l'initialisation du package communication", exc_info=True)
