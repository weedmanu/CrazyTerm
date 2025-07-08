"""
Gestionnaire des thèmes et couleurs pour CrazySerialTerm
Ce module contient toutes les fonctions liées aux thèmes visuels.
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
import logging

logger = logging.getLogger("CrazySerialTerm")

def setup_dark_palette():
    """
    Crée et retourne une palette de couleurs sombre pour l'application.
    
    Returns:
        QPalette: Palette de couleurs sombre
    """
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(42, 42, 42)) # Fond des zones de texte/liste
    dark_palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white) # Texte général
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    return dark_palette

def get_light_palette():
    """Retourne une palette de couleurs claire."""
    palette = QPalette()
    # Couleurs claires
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

def get_dark_palette():
    """Retourne une palette de couleurs sombre."""
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    return palette

def get_hacker_palette():
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

def apply_theme(theme_name):
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

# Couleurs prédéfinies pour les messages du terminal
TERMINAL_COLORS = {
    'system': QColor("orange"),
    'received': QColor("blue"),
    'sent': QColor("green"),
    'error': QColor("red"),
    'warning': QColor("yellow"),
    'info': QColor("cyan")
}

def get_theme_terminal_colors(theme_name):
    """
    Retourne les couleurs du terminal adaptées au thème.
    
    Args:
        theme_name (str): Nom du thème ('clair', 'sombre', 'hacker')
    
    Returns:
        dict: Dictionnaire des couleurs pour le terminal
    """
    if theme_name == 'clair':
        return {
            'text': QColor(0, 0, 0),          # Texte noir pour fond clair
            'background': QColor(255, 255, 255), # Fond blanc
            'received': QColor(0, 0, 255),    # Bleu foncé pour données reçues
            'sent': QColor(0, 128, 0),        # Vert foncé pour données envoyées
            'system': QColor(255, 140, 0),    # Orange pour messages système
            'error': QColor(220, 20, 60),     # Rouge foncé pour erreurs
            'warning': QColor(255, 165, 0),   # Orange pour avertissements
            'info': QColor(30, 144, 255)      # Bleu pour informations
        }
    elif theme_name == 'sombre':
        return {
            'text': QColor(255, 255, 255),    # Texte blanc pour fond sombre
            'background': QColor(42, 42, 42), # Fond gris sombre
            'received': QColor(100, 150, 255), # Bleu clair pour données reçues
            'sent': QColor(100, 255, 100),    # Vert clair pour données envoyées
            'system': QColor(255, 165, 0),    # Orange pour messages système
            'error': QColor(255, 100, 100),   # Rouge clair pour erreurs
            'warning': QColor(255, 255, 100), # Jaune clair pour avertissements
            'info': QColor(100, 255, 255)     # Cyan clair pour informations
        }
    elif theme_name == 'hacker':
        return {
            'text': QColor(0, 255, 0),        # Texte vert pour style hacker
            'background': QColor(0, 0, 0),    # Fond noir
            'received': QColor(50, 255, 50),  # Vert clair pour données reçues
            'sent': QColor(150, 255, 50),     # Vert-jaune pour données envoyées
            'system': QColor(255, 255, 0),    # Jaune pour messages système
            'error': QColor(255, 50, 50),     # Rouge-vert pour erreurs
            'warning': QColor(255, 255, 100), # Jaune clair pour avertissements
            'info': QColor(0, 255, 255)       # Cyan pour informations
        }
    else:
        # Thème par défaut (sombre)
        return get_theme_terminal_colors('sombre')

def save_custom_theme(theme_name, palette, terminal_colors):
    """
    Sauvegarde un thème personnalisé.
    
    Args:
        theme_name (str): Nom du thème
        palette (QPalette): Palette de couleurs
        terminal_colors (dict): Couleurs du terminal
    """
    try:
        from PyQt5.QtCore import QSettings
        settings = QSettings("CrazySerialTerm", "Themes")
        
        # Sauvegarder la palette
        settings.beginGroup(f"theme_{theme_name}")
        settings.setValue("window", palette.color(QPalette.Window).name())
        settings.setValue("windowText", palette.color(QPalette.WindowText).name())
        settings.setValue("base", palette.color(QPalette.Base).name())
        settings.setValue("text", palette.color(QPalette.Text).name())
        settings.setValue("button", palette.color(QPalette.Button).name())
        settings.setValue("buttonText", palette.color(QPalette.ButtonText).name())
        settings.setValue("highlight", palette.color(QPalette.Highlight).name())
        settings.setValue("highlightedText", palette.color(QPalette.HighlightedText).name())
        settings.endGroup()
        
        # Sauvegarder les couleurs du terminal
        settings.beginGroup(f"terminal_{theme_name}")
        for key, color in terminal_colors.items():
            if hasattr(color, 'name'):
                settings.setValue(key, color.name())
        settings.endGroup()
        
        logger.info(f"Thème personnalisé '{theme_name}' sauvegardé")
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du thème: {e}")

def load_custom_theme(theme_name):
    """
    Charge un thème personnalisé.
    
    Args:
        theme_name (str): Nom du thème
        
    Returns:
        tuple: (palette, terminal_colors) ou (None, None) si échec
    """
    try:
        from PyQt5.QtCore import QSettings
        settings = QSettings("CrazySerialTerm", "Themes")
        
        # Vérifier si le thème existe
        if not settings.contains(f"theme_{theme_name}/window"):
            return None, None
        
        # Charger la palette
        palette = QPalette()
        settings.beginGroup(f"theme_{theme_name}")
        palette.setColor(QPalette.Window, QColor(settings.value("window", "#353535")))
        palette.setColor(QPalette.WindowText, QColor(settings.value("windowText", "#ffffff")))
        palette.setColor(QPalette.Base, QColor(settings.value("base", "#2a2a2a")))
        palette.setColor(QPalette.Text, QColor(settings.value("text", "#ffffff")))
        palette.setColor(QPalette.Button, QColor(settings.value("button", "#353535")))
        palette.setColor(QPalette.ButtonText, QColor(settings.value("buttonText", "#ffffff")))
        palette.setColor(QPalette.Highlight, QColor(settings.value("highlight", "#2a82da")))
        palette.setColor(QPalette.HighlightedText, QColor(settings.value("highlightedText", "#000000")))
        settings.endGroup()
        
        # Charger les couleurs du terminal
        terminal_colors = {}
        settings.beginGroup(f"terminal_{theme_name}")
        color_keys = ['text', 'background', 'received', 'sent', 'system', 'error', 'warning', 'info']
        for key in color_keys:
            color_value = settings.value(key)
            if color_value:
                terminal_colors[key] = QColor(color_value)
        settings.endGroup()
        
        logger.info(f"Thème personnalisé '{theme_name}' chargé")
        return palette, terminal_colors
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement du thème: {e}")
        return None, None

def get_available_custom_themes():
    """
    Retourne la liste des thèmes personnalisés disponibles.
    
    Returns:
        list: Liste des noms de thèmes personnalisés
    """
    try:
        from PyQt5.QtCore import QSettings
        settings = QSettings("CrazySerialTerm", "Themes")
        themes = []
        
        for key in settings.allKeys():
            if key.startswith("theme_") and key.endswith("/window"):
                theme_name = key.replace("theme_", "").replace("/window", "")
                themes.append(theme_name)
                
        return themes
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des thèmes: {e}")
        return []

def delete_custom_theme(theme_name):
    """
    Supprime un thème personnalisé.
    
    Args:
        theme_name (str): Nom du thème à supprimer
    """
    try:
        from PyQt5.QtCore import QSettings
        settings = QSettings("CrazySerialTerm", "Themes")
        
        # Supprimer la palette
        settings.beginGroup(f"theme_{theme_name}")
        settings.remove("")
        settings.endGroup()
        
        # Supprimer les couleurs du terminal
        settings.beginGroup(f"terminal_{theme_name}")
        settings.remove("")
        settings.endGroup()
        
        logger.info(f"Thème personnalisé '{theme_name}' supprimé")
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du thème: {e}")

def reset_to_default_theme():
    """Remet le thème par défaut (sombre)."""
    try:
        app = QApplication.instance()
        if app:
            app.setPalette(get_dark_palette())
            logger.info("Thème réinitialisé au thème sombre par défaut")
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation du thème: {e}")
