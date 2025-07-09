#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module : theme_manager.py

Outil interne CrazyTerm : Gestionnaire de thèmes graphiques (non natif, chargé dynamiquement)

Rôle :
    Permet de personnaliser l’apparence de l’interface utilisateur de CrazyTerm (thèmes clair, sombre, hacker).
    Fournit les palettes de couleurs, l’application dynamique des thèmes, et la gestion centralisée des couleurs du terminal.

Fonctionnalités principales :
    - Application de thèmes PyQt5 (clair, sombre, hacker)
    - Gestion des palettes globales et couleurs du terminal
    - Méthodes pour rafraîchir l’affichage et appliquer les styles CSS
    - Interface pour la gestion future de thèmes personnalisés (JSON)
    - Robustesse, typage et journalisation

Dépendances :
    - PyQt5 (QtWidgets, QtGui)
    - typing
    - logging

Utilisation :
    Ce module est importé par la fenêtre principale et les gestionnaires d’UI pour appliquer dynamiquement les thèmes à l’application et au terminal.

Auteur :
    Projet CrazyTerm (2025) Manu
"""

from __future__ import annotations

from PyQt5.QtWidgets import QApplication, QTextEdit
from PyQt5.QtGui import QColor, QPalette
import logging
from typing import Dict, Optional, List, Any

__all__ = ["ThemeManager", "get_theme_terminal_colors"]

logger = logging.getLogger("CrazySerialTerm")

# --- Fonctions palettes globales ---
def get_light_palette() -> QPalette:
    """Retourne une palette de couleurs claire."""
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(0, 0, 255))
    palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    return palette

def get_dark_palette() -> QPalette:
    """Retourne une palette de couleurs sombre."""
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor('white'))
    palette.setColor(QPalette.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    palette.setColor(QPalette.ToolTipBase, QColor('white'))
    palette.setColor(QPalette.ToolTipText, QColor('white'))
    palette.setColor(QPalette.Text, QColor('white'))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor('white'))
    palette.setColor(QPalette.BrightText, QColor('red'))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor('black'))
    return palette

def get_hacker_palette() -> QPalette:
    """Retourne une palette de couleurs style 'hacker' (noir/vert)."""
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(0, 0, 0))
    palette.setColor(QPalette.WindowText, QColor(0, 255, 0))
    palette.setColor(QPalette.Base, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(0, 255, 0))
    palette.setColor(QPalette.Button, QColor(10, 30, 10))
    palette.setColor(QPalette.ButtonText, QColor(0, 255, 0))
    palette.setColor(QPalette.Highlight, QColor(0, 255, 0))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    return palette

def apply_theme(theme_name: str) -> None:
    """
    Applique un thème à l'application.
    Args:
        theme_name (str): Nom du thème ('clair', 'sombre', 'hacker')
    """
    app = QApplication.instance()
    if not app:
        logger.error("Aucune application QApplication active")
        return
    logger.info(f"Application du thème: {theme_name}")
    if theme_name == 'clair':
        app.setPalette(get_light_palette())
    elif theme_name == 'sombre':
        app.setPalette(get_dark_palette())
    elif theme_name == 'hacker':
        app.setPalette(get_hacker_palette())
    else:
        logger.warning(f"Thème inconnu: {theme_name}")

def get_theme_terminal_colors(theme_name: str) -> Dict[str, QColor]:
    """
    Retourne les couleurs du terminal pour un thème donné.
    Toutes les couleurs (reçu, envoyé, erreur, etc.) suivent le thème sélectionné.
    Args:
        theme_name (str): Nom du thème.
    Returns:
        Dict[str, QColor]: Dictionnaire des couleurs par type de message.
    """
    if theme_name == 'clair':
        return {
            'text': QColor(0, 0, 0),
            'background': QColor(255, 255, 255),
            'received': QColor(0, 0, 0),
            'sent': QColor(0, 0, 0),
            'system': QColor(0, 0, 0),
            'error': QColor(0, 0, 0),
            'warning': QColor(0, 0, 0),
            'info': QColor(0, 0, 0)
        }
    elif theme_name == 'sombre':
        return {
            'text': QColor(255, 255, 255),
            'background': QColor(42, 42, 42),
            'received': QColor(255, 255, 255),
            'sent': QColor(255, 255, 255),
            'system': QColor(255, 255, 255),
            'error': QColor(255, 255, 255),
            'warning': QColor(255, 255, 255),
            'info': QColor(255, 255, 255)
        }
    elif theme_name == 'hacker':
        return {
            'text': QColor(0, 255, 0),
            'background': QColor(0, 0, 0),
            'received': QColor(0, 255, 0),
            'sent': QColor(0, 255, 0),
            'system': QColor(0, 255, 0),
            'error': QColor(0, 255, 0),
            'warning': QColor(0, 255, 0),
            'info': QColor(0, 255, 0)
        }
    else:
        return get_theme_terminal_colors('sombre')

def reset_to_default_theme() -> None:
    """Remet le thème par défaut (sombre)."""
    try:
        app = QApplication.instance()
        if app:
            app.setPalette(get_dark_palette())
            logger.info("Thème réinitialisé au thème sombre par défaut")
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation du thème: {e}")

# --- Classe ThemeManager ---
class ThemeManager:
    """
    Gestionnaire de thèmes pour l'application CrazyTerm.
    Permet d'appliquer et de gérer les thèmes de l'interface.
    """
    def __init__(self, terminal_output: Optional[QTextEdit] = None) -> None:
        """
        Initialise le ThemeManager.
        Args:
            terminal_output (QTextEdit, optionnel): Widget de sortie du terminal.
        """
        self.terminal_output = terminal_output
        logger.info("ThemeManager initialisé")

    def apply_theme(self, theme_name: str) -> None:
        """
        Applique le thème spécifié à l'interface.
        Args:
            theme_name (str): Nom du thème à appliquer.
        """
        try:
            apply_theme(theme_name)
            if self.terminal_output and hasattr(self.terminal_output, 'terminal_buffer'):
                self.terminal_output.terminal_buffer.set_theme(theme_name)
                logger.info(f"Thème appliqué au terminal: {theme_name}")
        except Exception as e:
            logger.error(f"Erreur lors de l'application du thème: {e}")
            raise

    def refresh_terminal_display(self, theme_name: str) -> None:
        """
        Réapplique la couleur du thème courant à tout le texte du terminal.
        Utilise la même approche que l'ancien CrazySerialTerm avec les palettes + setStyleSheet.
        """
        if not self.terminal_output:
            return
        app = QApplication.instance()
        if app:
            if theme_name == 'clair':
                app.setPalette(get_light_palette())
                self.terminal_output.setStyleSheet("background-color: white; color: black;")
            elif theme_name == 'sombre':
                app.setPalette(get_dark_palette())
                self.terminal_output.setStyleSheet("background-color: rgb(42, 42, 42); color: white;")
            elif theme_name == 'hacker':
                app.setPalette(get_hacker_palette())
                self.terminal_output.setStyleSheet("background-color: black; color: rgb(0, 255, 0);")
        self.terminal_output.update()
        logger.info(f"Affichage du terminal rafraîchi pour le thème : {theme_name}")

    def save_custom_theme(self, theme_name: str, theme_data: Dict[str, Any]) -> None:
        """
        Sauvegarde un thème personnalisé dans le stockage JSON.
        Args:
            theme_name (str): Nom du thème.
            theme_data (dict): Données du thème à sauvegarder.
        """
        logger.warning("La sauvegarde des thèmes personnalisés n'est plus supportée (QSettings supprimé). À réimplémenter en JSON si besoin.")

    def load_custom_theme(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """
        Charge un thème personnalisé depuis le stockage JSON.
        Args:
            theme_name (str): Nom du thème à charger.
        Returns:
            Optional[Dict[str, Any]]: Données du thème ou None si absent.
        """
        logger.warning("Le chargement des thèmes personnalisés n'est plus supporté (QSettings supprimé). À réimplémenter en JSON si besoin.")
        return None

    def get_available_custom_themes(self) -> List[str]:
        """
        Retourne la liste des thèmes personnalisés disponibles.
        Returns:
            List[str]: Liste des noms de thèmes personnalisés.
        """
        logger.warning("La liste des thèmes personnalisés n'est plus supportée (QSettings supprimé). À réimplémenter en JSON si besoin.")
        return []

    def delete_custom_theme(self, theme_name: str) -> None:
        """
        Supprime un thème personnalisé du stockage JSON.
        Args:
            theme_name (str): Nom du thème à supprimer.
        """
        logger.warning("La suppression des thèmes personnalisés n'est plus supportée (QSettings supprimé). À réimplémenter en JSON si besoin.")
