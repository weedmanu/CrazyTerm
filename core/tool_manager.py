#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module : tool_manager.py

Outil interne CrazyTerm : Gestionnaire d’outils (non natif, chargé dynamiquement)

Rôle :
    Gère le chargement dynamique, l’intégration et la gestion centralisée de tous les outils internes
    et externes de CrazyTerm.

Fonctionnalités principales :
    - Découverte automatique des modules outils
    - Chargement dynamique et gestion des instances
    - Suivi des outils actifs et intégration à l’UI
    - Journalisation des opérations

Dépendances :
    - importlib
"""

import importlib
import glob
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ToolManager:
    """Gestionnaire des outils pour CrazyTerm."""
    
    def __init__(self, parent=None) -> None:
        """Initialise le gestionnaire d'outils dynamiquement avec parent Qt."""
        self.tools: Dict[str, Any] = {}
        self.active_tools: List[str] = []
        self.parent = parent
        self._load_dynamic_tools()
        
        logger.info("ToolManager initialisé (chargement dynamique)")
    
    def _load_dynamic_tools(self) -> None:
        """Scanne le dossier tools et importe dynamiquement tous les outils tool_*.py."""
        import os
        tools_dir = os.path.join(os.path.dirname(__file__), '..', 'tools')
        pattern = os.path.join(tools_dir, 'tool_*.py')
        for tool_path in glob.glob(pattern):
            module_name = os.path.splitext(os.path.basename(tool_path))[0]
            try:
                module = importlib.import_module(f'tools.{module_name}')
                tool_class = None
                # 1. Cherche une classe commençant par 'tool'
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if isinstance(obj, type) and attr.lower().startswith('tool'):
                        tool_class = obj
                        break
                # 2. Sinon, prend la première classe trouvée
                if not tool_class:
                    for attr in dir(module):
                        obj = getattr(module, attr)
                        if isinstance(obj, type) and not attr.startswith('__'):
                            tool_class = obj
                            break
                if tool_class:
                    # Import ici pour éviter les cycles
                    from PyQt5.QtWidgets import QDialog
                    if issubclass(tool_class, QDialog):
                        instance = tool_class(self.parent) if self.parent else tool_class()
                    else:
                        instance = tool_class()
                    self.register_tool(module_name, instance)
                    logger.info(f"Outil dynamique chargé: {module_name}")
            except Exception as e:
                logger.warning(f"Échec chargement outil {module_name}: {e}")
    
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
