"""UI Manager Module pour CrazyTerm."""

import logging
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

logger = logging.getLogger(__name__)


class UIManager:
    """Gestionnaire d'interface utilisateur pour CrazyTerm."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialise le gestionnaire d'interface utilisateur."""
        self.parent = parent
        self.widgets: Dict[str, QWidget] = {}
        self.layouts: Dict[str, Any] = {}
        
        logger.info("UIManager initialisé")
    
    def create_layout(self, layout_type: str = "vertical") -> Any:
        """Crée un layout selon le type spécifié."""
        if layout_type == "vertical":
            return QVBoxLayout()
        elif layout_type == "horizontal":
            return QHBoxLayout()
        else:
            return QVBoxLayout()
    
    def add_widget(self, name: str, widget: QWidget) -> None:
        """Ajoute un widget à la gestion."""
        self.widgets[name] = widget
        logger.debug(f"Widget '{name}' ajouté à UIManager")
    
    def get_widget(self, name: str) -> Optional[QWidget]:
        """Récupère un widget par son nom."""
        return self.widgets.get(name)
    
    def apply_theme(self, theme_name: str) -> None:
        """Applique un thème à l'interface."""
        logger.info(f"Thème '{theme_name}' appliqué")
    
    def __str__(self) -> str:
        """Retourne une représentation string de l'UIManager."""
        return f"UIManager(widgets={len(self.widgets)})"


logger.info("Module ui_manager initialisé")
