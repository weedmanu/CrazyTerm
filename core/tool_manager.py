"""Tool Manager Module pour CrazyTerm."""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ToolManager:
    """Gestionnaire des outils pour CrazyTerm."""
    
    def __init__(self) -> None:
        """Initialise le gestionnaire d'outils."""
        self.tools: Dict[str, Any] = {}
        self.active_tools: List[str] = []
        
        logger.info("ToolManager initialisé")
    
    def register_tool(self, name: str, tool: Any) -> None:
        """Enregistre un outil."""
        self.tools[name] = tool
        logger.debug(f"Outil '{name}' enregistré")
    
    def get_tool(self, name: str) -> Optional[Any]:
        """Récupère un outil par son nom."""
        return self.tools.get(name)
    
    def activate_tool(self, name: str) -> bool:
        """Active un outil."""
        if name in self.tools:
            if name not in self.active_tools:
                self.active_tools.append(name)
            logger.info(f"Outil '{name}' activé")
            return True
        return False
    
    def deactivate_tool(self, name: str) -> bool:
        """Désactive un outil."""
        if name in self.active_tools:
            self.active_tools.remove(name)
            logger.info(f"Outil '{name}' désactivé")
            return True
        return False
    
    def get_active_tools(self) -> List[str]:
        """Retourne la liste des outils actifs."""
        return self.active_tools.copy()
    
    def __str__(self) -> str:
        """Retourne une représentation string du ToolManager."""
        return f"ToolManager(tools={len(self.tools)}, active={len(self.active_tools)})"


logger.info("Module tool_manager initialisé")
