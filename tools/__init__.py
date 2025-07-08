"""
Package tools - Outils intégrés pour CrazySerialTerm.
Ce package contient les outils utilitaires comme le calculateur de checksum et le convertisseur de données.
"""

import logging
from typing import Optional
logger = logging.getLogger("CrazySerialTerm.tools")

# Exemple de type hint pour conformité
__tools_version__: Optional[str] = None

# Bloc de gestion d’erreur pour robustesse du package
try:
    pass
except Exception:
    logger.error("Erreur dans l'initialisation du package tools", exc_info=True)
