"""
Package core - Composants principaux de CrazySerialTerm.
Ce package contient le lanceur, la fenêtre principale et la configuration de l’application.
"""

import logging
from typing import Optional
logger = logging.getLogger("CrazySerialTerm.core")

# Exemple de type hint pour conformité
__core_version__: Optional[str] = None

# Bloc de gestion d’erreur pour robustesse du package
try:
    pass
except Exception:
    logger.error("Erreur dans l'initialisation du package core", exc_info=True)
