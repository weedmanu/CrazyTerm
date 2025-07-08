"""
Package interface - Interface utilisateur de CrazySerialTerm.
Ce package contient les composants graphiques et la gestion des thèmes de l’application.
"""

import logging
from typing import Optional
logger = logging.getLogger("CrazySerialTerm.interface")

# Exemple de type hint pour conformité
__interface_version__: Optional[str] = None

# Bloc de gestion d’erreur pour robustesse du package
try:
    pass
except Exception:
    logger.error("Erreur dans l'initialisation du package interface", exc_info=True)
