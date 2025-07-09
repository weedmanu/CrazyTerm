"""
Fenêtre principale de CrazySerialTerm - Version Série Simple
Ce module contient la classe principale de l'interface utilisateur série uniquement.

Classes :
    Terminal : Fenêtre principale de l'application, interface graphique et gestion des événements série.
"""

from __future__ import annotations

import os
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit,
                            QTabWidget, QStatusBar, QLabel, QMenu, QAction,
                            QFontDialog, QFileDialog,
                            QPushButton, QShortcut, QLineEdit, QComboBox, QGroupBox,
                            QCheckBox, QSpinBox, QGridLayout, QInputDialog, QMenuBar)
from PyQt5.QtGui import QColor, QTextCursor, QFont, QKeySequence, QTextCharFormat, QCloseEvent
from PyQt5.QtCore import Qt, QSettings, QTimer, QThread, pyqtSignal, QObject

from communication.serial_communication import RobustSerialManager
from interface.interface_components import (ConnectionPanel, InputPanel, AdvancedSettingsPanel)
from core.config_manager import SettingsManager
from interface.theme_manager import ThemeManager
from tools.tool_checksum import ChecksumCalculator
from tools.tool_converter import DataConverter
from system.memory_optimizer import get_ultra_memory_manager
from core.terminal_buffer import TerminalBufferManager
from core.tool_manager import ToolManager

logger = logging.getLogger("CrazySerialTerm")

class SendWorker(QThread):
    """
    Thread d'envoi asynchrone pour la communication série.
    """
    finished = pyqtSignal(bool, str, str)

    def __init__(self, serial_manager: RobustSerialManager, data: str, format_type: str, eol: str) -> None:
        """
        Initialise le thread d'envoi.
        """
        super().__init__()
        self.serial_manager = serial_manager
        self.data = data
        self.format_type = format_type
        self.eol = eol

    def run(self) -> None:
        """
        Exécute l'envoi asynchrone.
        """
        try:
            success = self.serial_manager.format_and_send(self.data, self.format_type, self.eol)
            self.finished.emit(success, "", self.data)
        except Exception as e:
            self.finished.emit(False, str(e), self.data)

class Terminal(QMainWindow):
    """
    Terminal de communication série simple avec interface graphique.
    Fenêtre principale de l'application.
    """
    
    # Constantes de classe
    PORT_CHECK_INTERVAL = 5000  # ms
    
    def __init__(self) -> None:
        """
        Initialise la fenêtre principale, les composants, les timers et l'interface utilisateur.
        """
        super().__init__()
        
        # Initialisation des composants
        self.serial_manager = RobustSerialManager()
        self.settings_manager = SettingsManager()
        
        # Gestionnaire mémoire ultra-optimisé
        self.ultra_memory = get_ultra_memory_manager()
        
        # Buffer des couleurs pour l'optimisation mémoire
        self._color_buffer: List[str] = []
        
        # Cache des formats de texte pour optimisation
        self._text_format_cache: Dict[str, Any] = {}
        
        # Configuration de base
        self.command_history: List[str] = []
        self.history_index: int = -1
        # self.settings = QSettings("SerialTerminal", "Settings")
        self.settings = SettingsManager
        self.log_file = None
        self.rx_bytes_count: int = 0
        self.tx_bytes_count: int = 0
        self.last_receive_time: Optional[datetime] = None
        
        # Interfaces utilisateur
        self.serial_panel: Optional[Any] = None
        self.input_panel: Optional[Any] = None
        self.advanced_panel: Optional[Any] = None
        
        # Terminal
        self.terminal_output: Optional[Any] = None
        self.tab_widget: Optional[Any] = None
        
        # Thème actuel
        self.theme_manager = ThemeManager(self.terminal_output)
        self.current_theme = 'sombre'  # Thème par défaut
        # Buffer manager pour le terminal
        self.terminal_buffer = None
        
        # Timer ultra-optimisé pour flush
        self._ultra_flush_timer = QTimer()
        self._ultra_flush_timer.timeout.connect(self._ultra_flush_buffer)
        self._ultra_flush_timer.start(200)  # Flush moins fréquent
        
        # Limite stricte de mémoire
        self._max_terminal_chars = 30000  # Limite ultra-stricte
        
        # Outils (instanciation unique, parenté correcte)
        self.tool_manager = ToolManager(self)
        
        # Timer pour l'envoi répété
        self.repeat_timer = QTimer()
        self.repeat_timer.timeout.connect(self.send_data)
        
        # Configuration de l'interface
        self.setupUI()
        self.setupMenus()  # Doit être appelé avant self.show() pour PyQt5
        self.setupStatusBar()
        self.setupShortcuts()
        self.connectSignals()

        # Timer pour vérifier les ports
        self.port_timer = QTimer()
        self.port_timer.timeout.connect(self.refresh_ports)
        self.port_timer.start(self.PORT_CHECK_INTERVAL)

        # Chargement des paramètres
        self.load_settings()

        # Appliquer les couleurs du terminal après initialisation
        self.theme_manager.apply_theme(self.current_theme)

        # Affichage de la fenêtre
        self.show()

        logger.info("Initialisation du terminal série")
    
    def setupUI(self) -> None:
        """
        Configure l'interface utilisateur principale (onglets, panneaux, widgets).
        """
        self.setWindowTitle("CrazySerialTerm - Terminal Série")
        self.setGeometry(100, 100, 1200, 800)
        # Widget central avec onglets
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        # Création explicite de la barre de menu (robustesse PyQt)
        if self.menuBar() is None:
            self.setMenuBar(QMenuBar(self))
        # Onglet principal avec terminal série
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        # Panneau de connexion série
        self.serial_panel = ConnectionPanel()
        main_layout.addWidget(self.serial_panel)
        # Sortie du terminal
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont("Consolas", 10))
        main_layout.addWidget(self.terminal_output)
        # Initialisation du buffer du terminal (corrige NoneType)
        self.terminal_buffer = TerminalBufferManager(self.terminal_output)
        # Synchronisation du buffer avec le ThemeManager
        self.terminal_output.terminal_buffer = self.terminal_buffer
        # Mettre à jour la référence terminal_output dans ThemeManager
        self.theme_manager.terminal_output = self.terminal_output
        
        # Panneau d'entrée
        self.input_panel = InputPanel()
        main_layout.addWidget(self.input_panel)
        # Ajouter l'onglet principal
        self.tab_widget.addTab(main_widget, "🔌 Terminal Série")
        # Onglet des paramètres avancés (créé mais pas encore ajouté)
        self.advanced_panel = AdvancedSettingsPanel()
        self.settings_tab_visible = False  # État par défaut : masqué
        self.settings_tab_index = None  # Index de l'onglet paramètres
        # L'onglet sera ajouté dans load_settings() selon les préférences
    
    def setupMenus(self) -> None:
        """
        Configure les menus de l'application (Terminal, Affichage, Outils, Thèmes).
        """
        # S'assurer que la barre de menu existe
        menubar = self.menuBar()
        if menubar is None:
            self.setMenuBar(QMenuBar(self))
            menubar = self.menuBar()
        if menubar is None:
            raise RuntimeError("Impossible d'initialiser la barre de menu (QMenuBar)")
        # Menu Terminal
        terminal_menu = menubar.addMenu('Terminal')
        if terminal_menu is None:
            raise RuntimeError("Impossible de créer le menu 'Terminal' (QMenu)")
        connect_action = QAction('Connecter', self)
        connect_action.setShortcut('Ctrl+O')
        connect_action.triggered.connect(self.connect_serial)
        terminal_menu.addAction(connect_action)
        disconnect_action = QAction('Déconnecter', self)
        disconnect_action.setShortcut('Ctrl+D')
        disconnect_action.triggered.connect(self.disconnect_serial)
        terminal_menu.addAction(disconnect_action)
        terminal_menu.addSeparator()
        clear_action = QAction('Effacer', self)
        clear_action.setShortcut('Ctrl+L')
        clear_action.triggered.connect(self.clear_terminal)
        terminal_menu.addAction(clear_action)
        # Menu Affichage
        view_menu = menubar.addMenu('Affichage')
        if view_menu is None:
            raise RuntimeError("Impossible de créer le menu 'Affichage' (QMenu)")
        self.toggle_send_panel_action = QAction('Afficher le panneau d\'envoi', self)
        self.toggle_send_panel_action.setCheckable(True)
        self.toggle_send_panel_action.setShortcut('Ctrl+T')
        self.toggle_send_panel_action.setChecked(True)
        self.toggle_send_panel_action.triggered.connect(self.toggle_send_panel_visibility)
        view_menu.addAction(self.toggle_send_panel_action)
        self.toggle_settings_tab_action = QAction('Afficher l\'onglet paramètres', self)
        self.toggle_settings_tab_action.setCheckable(True)
        self.toggle_settings_tab_action.setShortcut('Ctrl+Shift+S')
        self.toggle_settings_tab_action.setChecked(False)
        self.toggle_settings_tab_action.triggered.connect(self.toggle_settings_tab_visibility)
        view_menu.addAction(self.toggle_settings_tab_action)
        view_menu.addSeparator()
        themes_menu = view_menu.addMenu('Thèmes')
        if themes_menu is None:
            raise RuntimeError("Impossible de créer le menu 'Thèmes' (QMenu)")
        light_theme_action = QAction('Thème clair', self)
        light_theme_action.triggered.connect(lambda: self.change_theme('clair'))
        themes_menu.addAction(light_theme_action)
        dark_theme_action = QAction('Thème sombre', self)
        dark_theme_action.triggered.connect(lambda: self.change_theme('sombre'))
        themes_menu.addAction(dark_theme_action)
        hacker_theme_action = QAction('Thème hacker', self)
        hacker_theme_action.triggered.connect(lambda: self.change_theme('hacker'))
        themes_menu.addAction(hacker_theme_action)
        view_menu.addSeparator()
        font_action = QAction('Changer la police du terminal...', self)
        font_action.triggered.connect(self.change_font)
        view_menu.addAction(font_action)
        reset_view_action = QAction('Réinitialiser l\'apparence', self)
        reset_view_action.setToolTip("Réinitialise l'apparence au thème sombre par défaut")
        reset_view_action.triggered.connect(self.reset_config)
        view_menu.addAction(reset_view_action)
        # Menu Outils
        tools_menu = menubar.addMenu('Outils')
        if tools_menu is None:
            raise RuntimeError("Impossible de créer le menu 'Outils' (QMenu)")
        # --- Menu Outils dynamique amélioré ---
        from PyQt5.QtWidgets import QMessageBox
        # Tri alphabétique des outils
        for tool_name in sorted(self.tool_manager.tools.keys()):
            tool_instance = self.tool_manager.tools[tool_name]
            display_name = tool_name.replace('tool_', '').replace('_', ' ').capitalize()
            action = QAction(display_name, self)
            if hasattr(tool_instance, 'show'):
                action.triggered.connect(tool_instance.show)
            else:
                def show_error(name: str = display_name) -> None:
                    """
                    Affiche un message d'erreur si l'outil ne possède pas de fenêtre graphique.
                    Args:
                        name (str): Nom de l'outil.
                    Returns:
                        None
                    """
                    QMessageBox.warning(self, "Outil non disponible", f"L’outil '{name}' ne possède pas de fenêtre graphique (méthode show absente).")
                action.triggered.connect(show_error)
            tools_menu.addAction(action)
        # --- Fin menu Outils dynamique amélioré ---
    
    def setupStatusBar(self) -> None:
        """
        Configure la barre de statut de l'application.
        """
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Labels de statut
        self.connection_status_label = QLabel("Déconnecté")
        self.port_label = QLabel("Aucun port")
        self.bytes_label = QLabel("Octets: 0 ↑ / 0 ↓")
        
        self.status_bar.addWidget(self.connection_status_label)
        self.status_bar.addPermanentWidget(self.port_label)
        self.status_bar.addPermanentWidget(self.bytes_label)
    
    def connectSignals(self) -> None:
        """
        Connecte tous les signaux nécessaires de manière thread-safe.
        """
        try:
            # Signaux du panneau série
            self.serial_panel.connect_requested.connect(self.connect_serial)
            self.serial_panel.disconnect_requested.connect(self.disconnect_serial)
            self.serial_panel.refresh_requested.connect(self.refresh_ports)
            self.serial_panel.clear_requested.connect(self.clear_terminal)
            
            # Signaux du panneau d'entrée
            self.input_panel.send_requested.connect(self.send_data)
            
            # Signaux du panneau des paramètres avancés
            self.advanced_panel.send_settings_changed.connect(self.on_send_settings_changed)
            self.advanced_panel.display_settings_changed.connect(self.on_display_settings_changed)
            self.advanced_panel.serial_settings_changed.connect(self.on_serial_settings_changed)
            
            # Signaux du gestionnaire série robuste - Thread-safe via Qt
            self.serial_manager.data_received.connect(self.on_data_received, Qt.QueuedConnection)
            self.serial_manager.connection_changed.connect(self.on_connection_changed, Qt.QueuedConnection)
            self.serial_manager.error_occurred.connect(self.on_error_occurred, Qt.QueuedConnection)
            self.serial_manager.statistics_updated.connect(self.on_statistics_updated, Qt.QueuedConnection)
            
            logger.debug("Tous les signaux connectés avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la connexion des signaux: {e}")
            raise
    
    def connect_serial(self) -> None:
        """
        Établit la connexion série à partir des paramètres du panneau de connexion.
        """
        try:
            params = self.serial_panel.get_connection_params()
            if self.serial_manager.connect(params['port'], baudrate=params['baudrate']):
                self.append_text(f"[Système] Connecté au port {params['port']} à {params['baudrate']} bauds\n", 'system')
                self.serial_panel.set_connected(True)
            else:
                self.append_text("[Système] Échec de la connexion série\n", 'error')
        except Exception as e:
            self.append_text(f"[Système] Erreur de connexion: {str(e)}\n", 'error')
            logger.error(f"Erreur de connexion série: {str(e)}")
    
    def disconnect_serial(self) -> None:
        """
        Ferme la connexion série et met à jour l'interface.
        """
        try:
            self.serial_manager.disconnect_port()
            self.append_text("[Système] Déconnecté\n", 'system')
            self.serial_panel.set_connected(False)
        except Exception as e:
            self.append_text(f"[Système] Erreur de déconnexion: {str(e)}\n", 'error')
            logger.error(f"Erreur de déconnexion série: {str(e)}")
    
    def send_data(self, data: str, format_type: str = 'text') -> None:
        """
        Envoie des données via la connexion série.
        Toute la logique de formatage (EOL, hex/text) est désormais gérée côté communication.
        Args:
            data (str): Données à envoyer.
            format_type (str): Format d'envoi ('text' ou 'hex').
        """
        logger.info(f"[DEBUG] Slot send_data appelé avec data='{data}' format_type='{format_type}'")
        if not self.serial_manager.is_connected():
            self.append_text("[Système] Aucune connexion active\n", 'system')
            return
        # Validation des données d'entrée
        if not data or not isinstance(data, str):
            self.append_text("[Système] Données invalides\n", 'error')
            return
        if len(data) > 1024: # Limite de taille
            self.append_text("[Système] Données trop longues (max 1024 caractères)\n", 'error')
            return
        try:
            # Récupérer les paramètres d'envoi avancés si activés
            if self.advanced_panel.send_group.isChecked():
                send_settings = self.advanced_panel.get_send_settings()
                format_type = send_settings.get('format', 'ASCII').lower()
                eol = send_settings.get('eol', 'Aucun')
            else:
                format_type = 'text'
                eol = 'Aucun'
            # Utilisation d'un QThread pour l'envoi (formatage côté communication)
            self.send_worker = SendWorker(self.serial_manager, data, format_type, eol)
            self.send_worker.finished.connect(self._on_send_finished)
            self.send_worker.start()
            # Historique log si activé
            self.log_terminal_event('envoyé', data)
        except Exception as e:
            self.append_text(f"Erreur d'envoi: {str(e)}\n", 'error')
            logger.error(f"Erreur d'envoi de données: {str(e)}")

    def _on_send_finished(self, success: bool, error_msg: str, data: str) -> None:
        """
        Slot appelé à la fin de l'envoi asynchrone de données.
        Affiche le résultat dans le terminal et efface la barre d'envoi.
        Args:
            success (bool): Statut de l'envoi.
            error_msg (str): Message d'erreur éventuel.
            data (str): Données envoyées.
        Returns:
            None
        """
        if not success:
            self.append_text(f"Échec de l'envoi des données: {error_msg}\n", 'error')
        else:
            self.append_text(data, 'sent')
        # Efface la barre d'envoi après chaque commande
        if self.input_panel:
            self.input_panel.clear_input()
        self.send_worker = None
        logger.info(f"[DEBUG] Slot _on_send_finished appelé, success={success}, error_msg='{error_msg}'")
    
    def on_connection_changed(self, connected: bool) -> None:
        """
        Slot appelé lors d'un changement d'état de connexion série.
        """
        self.update_connection_status(connected)

    def on_data_received(self, data: bytes) -> None:
        """
        Slot appelé lors de la réception de données sur le port série.
        Args:
            data (bytes): Données reçues.
        """
        logger.info(f"[DEBUG] Slot on_data_received appelé, {len(data)} octets reçus")
        try:
            # Décodage et nettoyage
            text = data.decode('utf-8', errors='replace')
            clean_text = self.clean_received_text(text)
            self.append_text(clean_text, 'received')
            # Mise à jour des statistiques
            if hasattr(self, 'update_bytes_counter'):
                self.update_bytes_counter(received=len(data))
            self.log_terminal_event('reçu', clean_text)
        except Exception as e:
            logger.error(f"Erreur lors du traitement des données reçues: {e}")

    def on_error_occurred(self, error_message: str) -> None:
        """
        Slot appelé lors d'une erreur série.
        """
        self.append_text(f"[Erreur] {error_message}\n", 'error')

    def on_statistics_updated(self, stats: dict) -> None:
        """
        Slot appelé lors de la mise à jour des statistiques série.
        """
        rx = stats.get('rx_bytes', 0) if isinstance(stats, dict) else 0
        tx = stats.get('tx_bytes', 0) if isinstance(stats, dict) else 0
        if hasattr(self, 'bytes_label') and self.bytes_label:
            self.bytes_label.setText(f"Octets: {tx} ↑ / {rx} ↓")
        else:
            logger.warning("bytes_label absent lors de la mise à jour des statistiques")
    
    # Correction des signatures et docstrings pour les dernières méthodes publiques
    def on_data_received(self, data: bytes) -> None:
        """
        Slot appelé lors de la réception de données sur le port série.
        Args:
            data (bytes): Données reçues.
        """
        logger.info(f"[DEBUG] Slot on_data_received appelé, {len(data)} octets reçus")
        try:
            # Décodage et nettoyage
            text = data.decode('utf-8', errors='replace')
            clean_text = self.clean_received_text(text)
            self.append_text(clean_text, 'received')
            # Mise à jour des statistiques
            if hasattr(self, 'update_bytes_counter'):
                self.update_bytes_counter(received=len(data))
        except Exception as e:
            logger.error(f"Erreur lors du traitement des données reçues: {e}")
            raise

    def clean_received_text(self, text: str) -> str:
        """
        Nettoie le texte reçu en supprimant les caractères indésirables et séquences ANSI.
        Args:
            text (str): Texte à nettoyer.
        Returns:
            str: Texte nettoyé.
        """
        # Liste des caractères à supprimer
        chars_to_remove = [
            '←',     # Caractère flèche gauche
            '\x08',  # Backspace
            '\x7f',  # Delete
            '\x1b',  # Escape
        ]
        
        # Supprimer chaque caractère indésirable
        for char in chars_to_remove:
            text = text.replace(char, '')
        
        # Supprimer les séquences d'échappement ANSI courantes
        text = re.sub(r'\x1b\[[0-9;]*[mK]', '', text)
        
        return text

    def update_connection_status(self, connected: bool) -> None:
        """
        Met à jour l'affichage et l'état de la connexion série dans la barre de statut et le panneau de connexion.
        Args:
            connected (bool): True si connecté, False sinon.
        Returns:
            None
        """
        try:
            palette = self.connection_status_label.palette()
            if connected:
                self.connection_status_label.setText("Connecté")
                palette.setColor(self.connection_status_label.foregroundRole(), QColor('green'))
                self.connection_status_label.setPalette(palette)
                port = self.serial_panel.get_connection_params()['port']
                self.port_label.setText(f"Port: {port}")
                self.serial_panel.set_connected(True)
            else:
                self.connection_status_label.setText("Déconnecté")
                palette.setColor(self.connection_status_label.foregroundRole(), QColor('red'))
                self.connection_status_label.setPalette(palette)
                self.port_label.setText("Aucun port")
                self.serial_panel.set_connected(False)
                self.refresh_ports()
            logger.info(f"État de connexion mis à jour: {'Connecté' if connected else 'Déconnecté'}")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'état de connexion: {e}")

    def change_theme(self, theme_name: str) -> None:
        """
        Change le thème de l'application via ThemeManager.
        """
        try:
            self.theme_manager.apply_theme(theme_name)
            self.current_theme = theme_name
            # Synchronise le buffer du terminal avec le nouveau thème
            if hasattr(self, 'terminal_buffer') and self.terminal_buffer:
                self.terminal_buffer.set_theme(theme_name)
            self.refresh_terminal_display()  # Forcer le rafraîchissement
            self.settings.save_setting('theme', theme_name)  # Persistance via JSON
            logger.info(f"Thème changé: {theme_name}")
        except Exception as e:
            logger.error(f"Erreur lors du changement de thème: {e}")

    def apply_terminal_colors(self) -> None:
        """
        Applique les couleurs du terminal via ThemeManager.
        """
        try:
            self.theme_manager.apply_theme(self.current_theme)
        except Exception as e:
            logger.error(f"Erreur lors de l'application des couleurs: {e}")

    def refresh_terminal_display(self) -> None:
        """
        Force la mise à jour visuelle du terminal avec les nouvelles couleurs via ThemeManager.
        """
        try:
            self.theme_manager.refresh_terminal_display(self.current_theme)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du terminal: {e}")

    def apply_theme(self, theme_name: str) -> None:
        """
        Applique un thème à l'application via ThemeManager.
        """
        self.change_theme(theme_name)

    def load_settings(self) -> None:
        """
        Charge tous les paramètres utilisateur (thème, UI, groupes, options avancées, taille/fenêtre, police, panneaux) depuis le JSON centralisé.
        """
        try:
            # Thème
            theme = self.settings.load_setting('theme', 'sombre')
            if theme in ['clair', 'sombre', 'hacker']:
                self.change_theme(theme)
            # Paramètres avancés (groupes, options, log...)
            advanced_settings = self.settings.load_setting('advanced_settings', None)
            if advanced_settings and self.advanced_panel:
                self.advanced_panel.set_all_settings(advanced_settings)
            # Visibilité des panneaux
            send_panel_visible = self.settings.load_setting('send_panel_visible', True)
            if self.input_panel:
                self.input_panel.setVisible(send_panel_visible)
                # Synchroniser la case à cocher avec la visibilité réelle
                if self.toggle_send_panel_action:
                    self.toggle_send_panel_action.setChecked(send_panel_visible)
                    if send_panel_visible:
                        self.toggle_send_panel_action.setText('Masquer le panneau d\'envoi')
                    else:
                        self.toggle_send_panel_action.setText('Afficher le panneau d\'envoi')
            if self.advanced_panel:
                settings_tab_visible = advanced_settings.get('settings_tab_visible', False) if advanced_settings else False
                if settings_tab_visible and not self.settings_tab_visible:
                    self.toggle_settings_tab_visibility()
                elif not settings_tab_visible and self.settings_tab_visible:
                    self.toggle_settings_tab_visibility()
            # Taille et position de la fenêtre
            geometry = self.settings.load_setting('window_geometry', None)
            if geometry:
                self.setGeometry(*geometry)
            # Police du terminal
            font_data = self.settings.load_setting('terminal_font', None)
            if font_data and self.terminal_output:
                font = QFont(font_data.get('family', 'Consolas'), font_data.get('size', 10))
                self.terminal_output.setFont(font)
        except Exception as e:
            logger.error(f"Erreur lors du chargement des paramètres: {e}")

    def save_settings(self) -> None:
        """
        Sauvegarde tous les paramètres utilisateur (thème, UI, groupes, options avancées, taille/fenêtre, police, panneaux) dans le JSON centralisé.
        """
        try:
            self.settings.save_setting('theme', getattr(self, 'current_theme', 'sombre'))
            # Paramètres avancés (groupes, options, log...)
            if self.advanced_panel:
                advanced_settings = self.advanced_panel.get_all_settings()
                # Sauvegarder la visibilité de l'onglet paramètres
                advanced_settings['settings_tab_visible'] = self.settings_tab_visible
                self.settings.save_setting('advanced_settings', advanced_settings)
            # Visibilité du panneau d'envoi
            if self.input_panel:
                self.settings.save_setting('send_panel_visible', self.input_panel.isVisible())
            # Taille et position de la fenêtre
            geometry = (self.x(), self.y(), self.width(), self.height())
            self.settings.save_setting('window_geometry', geometry)
            # Police du terminal
            if self.terminal_output:
                font = self.terminal_output.font()
                font_data = {'family': font.family(), 'size': font.pointSize()}
                self.settings.save_setting('terminal_font', font_data)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des paramètres: {e}")
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Gère la fermeture de l'application de manière ultra-robuste avec nettoyage mémoire complet.
        Args:
            event (QCloseEvent): Événement de fermeture de la fenêtre.
        Returns:
            None
        """
        try:
            logger.info("Fermeture de l'application en cours...")
            # Arrêt de tous les timers (y compris mémoire)
            self._stop_all_timers_and_memory_cleanup()
            # 2. Flush final du buffer de texte
            try:
                if hasattr(self, '_pending_text_buffer') and self._pending_text_buffer:
                    self._flush_text_buffer()
                    logger.debug("Buffer de texte final flushé")
            except Exception as e:
                logger.warning(f"Erreur flush final: {e}")
            
            # 3. Fermer les connexions série de manière propre
            if hasattr(self, 'serial_manager') and self.serial_manager:
                try:
                    if self.serial_manager.is_connected():
                        logger.info("Déconnexion du port série...")
                        self.serial_manager.disconnect_port()
                        
                        # Attendre un peu pour la déconnexion propre
                        from PyQt5.QtCore import QEventLoop, QTimer
                        loop = QEventLoop()
                        QTimer.singleShot(200, loop.quit)
                        loop.exec_()
                        
                except Exception as e:
                    logger.error(f"Erreur lors de la déconnexion série: {str(e)}")
            
            # 4. Sauvegarder les paramètres
            try:
                self.save_settings()
                logger.debug("Paramètres sauvegardés")
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
            
            # 5. Fermer les fenêtres des outils
            tools_to_close = []
            if hasattr(self, 'checksum_calculator') and self.checksum_calculator:
                tools_to_close.append(('checksum_calculator', self.checksum_calculator))
            if hasattr(self, 'data_converter') and self.data_converter:
                tools_to_close.append(('data_converter', self.data_converter))
                
            for tool_name, tool in tools_to_close:
                try:
                    if hasattr(tool, 'close'):
                        tool.close()
                        logger.debug(f"Outil {tool_name} fermé")
                except Exception as e:
                    logger.warning(f"Erreur fermeture {tool_name}: {e}")
            
            # 6. Nettoyage mémoire ultra-complet
            try:
                # Vider et nettoyer le terminal
                if hasattr(self, 'terminal_output') and self.terminal_output:
                    self.terminal_output.clear()
                    self.terminal_output.deleteLater()
                    
                # Nettoyer les caches
                if hasattr(self, '_text_format_cache'):
                    self._text_format_cache.clear()
                if hasattr(self, '_pending_text_buffer'):
                    self._pending_text_buffer.clear()
                    
                # Nettoyer l'historique des commandes
                if hasattr(self, 'command_history'):
                    self.command_history.clear()
                    
                # Forcer le garbage collection multiple fois
                import gc
                for _ in range(3):
                    gc.collect()
                    
                logger.debug("Nettoyage mémoire complet effectué")
                
            except Exception as e:
                logger.warning(f"Erreur lors du nettoyage final: {e}")
            
            event.accept()
            logger.info("Application fermée proprement avec nettoyage complet")
            
        except Exception as e:
            logger.error(f"Erreur critique lors de la fermeture: {str(e)}")
            # En cas d'erreur critique, forcer la fermeture avec nettoyage d'urgence
            try:
                # Arrêt d'urgence des timers
                if hasattr(self, 'port_timer'):
                    self.port_timer.stop()
                if hasattr(self, 'repeat_timer'):
                    self.repeat_timer.stop()
                if hasattr(self, '_update_timer'):
                    self._update_timer.stop()
                    
                # Nettoyage d'urgence
                import gc
                gc.collect()
            except:
                pass
            event.accept()
    
    def _stop_all_timers_and_memory_cleanup(self) -> None:
        """
        Arrête tous les timers (y compris mémoire) et loggue l'état pour robustesse maximale.
        """
        try:
            timers = []
            if hasattr(self, 'port_timer') and self.port_timer:
                timers.append(('port_timer', self.port_timer))
            if hasattr(self, 'repeat_timer') and self.repeat_timer:
                timers.append(('repeat_timer', self.repeat_timer))
            if hasattr(self, '_update_timer') and self._update_timer:
                timers.append(('update_timer', self._update_timer))
            if hasattr(self, '_ultra_flush_timer') and self._ultra_flush_timer:
                timers.append(('ultra_flush_timer', self._ultra_flush_timer))
            # Arrêt du timer mémoire si présent
            if hasattr(self, 'ultra_memory') and hasattr(self.ultra_memory, '_cleanup_timer'):
                timers.append(('memory_cleanup_timer', self.ultra_memory._cleanup_timer))
            for timer_name, timer in timers:
                try:
                    if timer.isActive():
                        timer.stop()
                        logger.debug(f"Timer {timer_name} arrêté")
                except Exception as e:
                    logger.warning(f"Erreur arrêt timer {timer_name}: {e}")
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt des timers: {e}")

    def on_send_settings_changed(self, settings: Dict[str, Any]) -> None:
        """
        Traite les changements de paramètres d'envoi.
        Args:
            settings (Dict[str, Any]): Paramètres d'envoi modifiés.
        Returns:
            None
        """
        try:
            # ...traitement des paramètres d'envoi...
            pass
        except Exception as e:
            logger.error(f"Erreur lors du changement des paramètres d'envoi : {str(e)}")
            raise

    def on_display_settings_changed(self, settings: Dict[str, Any]) -> None:
        """
        Traite les changements de paramètres d'affichage.
        Args:
            settings (Dict[str, Any]): Paramètres d'affichage modifiés.
        Returns:
            None
        """
        try:
            # ...traitement des paramètres d'affichage...
            pass
        except Exception as e:
            logger.error(f"Erreur lors du changement des paramètres d'affichage : {str(e)}")
            raise

    def on_serial_settings_changed(self, settings: Dict[str, Any]) -> None:
        """
        Traite les changements de paramètres série.
        Args:
            settings (Dict[str, Any]): Paramètres série modifiés.
        Returns:
            None
        """
        try:
            # ...traitement des paramètres série...
            pass
        except Exception as e:
            logger.error(f"Erreur lors du changement des paramètres série : {str(e)}")
            raise
    
    def change_theme(self, theme_name: str) -> None:
        """
        Change le thème de l'application via ThemeManager.
        """
        try:
            self.theme_manager.apply_theme(theme_name)
            self.current_theme = theme_name
            # Synchronise le buffer du terminal avec le nouveau thème
            if hasattr(self, 'terminal_buffer') and self.terminal_buffer:
                self.terminal_buffer.set_theme(theme_name)
            self.refresh_terminal_display()  # Forcer le rafraîchissement
            self.settings.save_setting('theme', theme_name)  # Persistance via JSON
            logger.info(f"Thème changé: {theme_name}")
        except Exception as e:
            logger.error(f"Erreur lors du changement de thème: {e}")

    def apply_terminal_colors(self) -> None:
        """
        Applique les couleurs du terminal via ThemeManager.
        """
        try:
            self.theme_manager.apply_theme(self.current_theme)
        except Exception as e:
            logger.error(f"Erreur lors de l'application des couleurs: {e}")

    def refresh_terminal_display(self) -> None:
        """
        Force la mise à jour visuelle du terminal avec les nouvelles couleurs via ThemeManager.
        """
        try:
            self.theme_manager.refresh_terminal_display(self.current_theme)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du terminal: {e}")

    def apply_theme(self, theme_name: str) -> None:
        """
        Applique un thème à l'application via ThemeManager.
        """
        self.change_theme(theme_name)

    def _ultra_flush_buffer(self) -> None:
        """
        Flush ultra-optimisé utilisant le gestionnaire mémoire avancé avec gestion des couleurs.
        Returns:
            None
        """
        try:
            if hasattr(self, 'ultra_memory') and hasattr(self, 'terminal_output'):
                if self.terminal_output and hasattr(self, '_color_buffer'):
                    # Flush le buffer texte via le gestionnaire mémoire ultra
                    self.ultra_memory.flush_buffer(self.terminal_output)
                    
                    # Nettoyer le buffer des couleurs
                    if hasattr(self, '_color_buffer'):
                        self._color_buffer.clear()
                    
                    # Vérifier et nettoyer si nécessaire
                    stats = self.ultra_memory.get_memory_stats()
                    if stats['current_objects'] > 40:
                        logger.warning(f"Trop d'objets en mémoire: {stats['current_objects']}")
                        self.ultra_memory.emergency_cleanup()
        except Exception as e:
            logger.error(f"Erreur dans _ultra_flush_buffer: {e}")

    def toggle_send_panel_visibility(self) -> None:
        """
        Masque ou affiche le panneau d'envoi.
        """
        try:
            is_visible = self.input_panel.isVisible()
            new_visible = not is_visible
            self.input_panel.setVisible(new_visible)
            # Synchroniser la case à cocher avec la visibilité réelle
            if self.toggle_send_panel_action:
                self.toggle_send_panel_action.setChecked(new_visible)
                if new_visible:
                    self.toggle_send_panel_action.setText('Masquer le panneau d\'envoi')
                else:
                    self.toggle_send_panel_action.setText('Afficher le panneau d\'envoi')
            # Sauvegarder les paramètres
            self.save_settings()
            logger.info(f"Panneau d'envoi {'affiché' if new_visible else 'masqué'}")
        except Exception as e:
            logger.error(f"Erreur lors du basculement du panneau d'envoi: {str(e)}")

    def toggle_settings_tab_visibility(self) -> None:
        """
        Masque ou affiche l'onglet des paramètres.
        """
        try:
            if self.settings_tab_visible and self.settings_tab_index is not None:
                # Masquer l'onglet des paramètres
                self.tab_widget.removeTab(self.settings_tab_index)
                self.toggle_settings_tab_action.setText('Afficher l\'onglet paramètres')
                self.toggle_settings_tab_action.setChecked(False)
                self.settings_tab_visible = False
                self.settings_tab_index = None
                logger.info("Onglet paramètres masqué")
            else:
                # Afficher l'onglet des paramètres
                self.settings_tab_index = self.tab_widget.addTab(self.advanced_panel, "⚙️ Paramètres")
                self.toggle_settings_tab_action.setText('Masquer l\'onglet paramètres')
                self.toggle_settings_tab_action.setChecked(True)
                self.settings_tab_visible = True
                logger.info("Onglet paramètres affiché")
            # Sauvegarder les paramètres
            self.save_settings()
        except Exception as e:
            logger.error(f"Erreur lors du basculement de l'onglet paramètres: {str(e)}")

    def reset_config(self) -> None:
        """
        Réinitialise l'apparence de l'application (thème sombre, police par défaut, onglet paramètres masqué).
        """
        try:
            self.change_theme('sombre')
            self.terminal_output.setFont(QFont("Consolas", 10))
            if self.settings_tab_visible and self.settings_tab_index is not None:
                self.tab_widget.removeTab(self.settings_tab_index)
                self.settings_tab_visible = False
                self.settings_tab_index = None
                self.toggle_settings_tab_action.setChecked(False)
                self.toggle_settings_tab_action.setText('Afficher l\'onglet paramètres')
            self.save_settings()
            logger.info("Apparence réinitialisée (thème sombre, police par défaut, onglet paramètres masqué)")
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation de l'apparence: {e}")

    def setupShortcuts(self) -> None:
        """
        Initialise les raccourcis clavier de l'application (placeholder).
        """
        pass

    def clear_terminal(self) -> None:
        """
        Efface le contenu du terminal.
        """
        if hasattr(self, 'terminal_output') and self.terminal_output:
            self.terminal_output.clear()
        else:
            logger.warning("terminal_output absent lors de l'effacement")

    def change_font(self) -> None:
        """
        Ouvre une boîte de dialogue pour choisir la police du terminal.
        """
        from PyQt5.QtWidgets import QFontDialog
        if hasattr(self, 'terminal_output') and self.terminal_output:
            font, ok = QFontDialog.getFont(self.terminal_output.font(), self, "Choisir la police du terminal")
            if ok:
                self.terminal_output.setFont(font)
        else:
            logger.warning("terminal_output absent lors du changement de police")

    def show_checksum_calculator(self) -> None:
        """
        Affiche la fenêtre du calculateur de checksum.
        """
        if hasattr(self, 'checksum_calculator') and self.checksum_calculator:
            self.checksum_calculator.show()
            self.checksum_calculator.raise_()
            self.checksum_calculator.activateWindow()
        else:
            logger.error("ChecksumCalculator non instancié")

    def show_data_converter(self) -> None:
        """
        Affiche la fenêtre du convertisseur de données.
        """
        if hasattr(self, 'data_converter') and self.data_converter:
            self.data_converter.show()
            self.data_converter.raise_()
            self.data_converter.activateWindow()
        else:
            logger.error("DataConverter non instancié")

    def refresh_ports(self) -> None:
        """
        Rafraîchit la liste des ports série disponibles dans le panneau de connexion.
        """
        if hasattr(self, 'serial_panel') and self.serial_panel and hasattr(self.serial_panel, 'refresh_ports'):
            self.serial_panel.refresh_ports()
        else:
            logger.warning("serial_panel ou sa méthode refresh_ports est absente")

    def append_text(self, text: str, msg_type: str = 'system') -> None:
        """
        Affiche du texte dans le terminal avec un style/couleur selon le type de message et le thème courant.
        Args:
            text (str): Texte à afficher.
            msg_type (str): Type de message ('system', 'error', 'received', etc.).
        """
        if not hasattr(self, 'terminal_output') or self.terminal_output is None:
            logger.warning("terminal_output absent lors de l'affichage du texte")
            return
        from PyQt5.QtGui import QTextCursor
        # Utiliser uniquement insertPlainText pour que la couleur soit gérée par la palette globale
        # et le setStyleSheet appliqué dans ThemeManager
        try:
            cursor = self.terminal_output.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(text)
            self.terminal_output.setTextCursor(cursor)
            self.terminal_output.ensureCursorVisible()
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage du texte dans le terminal: {e}")

__all__ = ["Terminal", "SendWorker"]
