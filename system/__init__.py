"""
Package system - Système et optimisation
Contient les utilitaires système, gestion d'erreurs et optimisation mémoire.
"""

import logging
from typing import Optional
logger = logging.getLogger("CrazySerialTerm.system")

# Exemple de type hint pour conformité
__system_version__: Optional[str] = None

# Bloc de gestion d’erreur pour robustesse du package
try:
    pass
except Exception:
    logger.error("Erreur dans l'initialisation du package system", exc_info=True)
