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
from PyQt5.QtCore import Qt, QSettings, QTimer

from communication.serial_communication import RobustSerialManager
from interface.interface_components import (ConnectionPanel, InputPanel, AdvancedSettingsPanel)
from core.config_manager import SettingsManager
from interface.theme_manager import apply_theme
from tools.tool_checksum import ChecksumCalculator
from tools.tool_converter import DataConverter
from system.memory_optimizer import get_ultra_memory_manager

logger = logging.getLogger("CrazySerialTerm")

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
        self.settings = QSettings("SerialTerminal", "Settings")
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
        self.current_theme = 'sombre'  # Thème par défaut
        
        # Timer ultra-optimisé pour flush
        self._ultra_flush_timer = QTimer()
        self._ultra_flush_timer.timeout.connect(self._ultra_flush_buffer)
        self._ultra_flush_timer.start(200)  # Flush moins fréquent
        
        # Limite stricte de mémoire
        self._max_terminal_chars = 30000  # Limite ultra-stricte
        
        # Outils
        self.checksum_calculator = ChecksumCalculator()
        self.data_converter = DataConverter()
        
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
        self.apply_terminal_colors()

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
        light_theme_action.triggered.connect(lambda: self.apply_theme('clair'))
        themes_menu.addAction(light_theme_action)
        dark_theme_action = QAction('Thème sombre', self)
        dark_theme_action.triggered.connect(lambda: self.apply_theme('sombre'))
        themes_menu.addAction(dark_theme_action)
        hacker_theme_action = QAction('Thème hacker', self)
        hacker_theme_action.triggered.connect(lambda: self.apply_theme('hacker'))
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
        checksum_action = QAction('Calculateur de Checksum', self)
        checksum_action.triggered.connect(self.show_checksum_calculator)
        tools_menu.addAction(checksum_action)
        converter_action = QAction('Convertisseur de Données', self)
        converter_action.triggered.connect(self.show_data_converter)
        tools_menu.addAction(converter_action)
    
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
        Args:
            data (str): Données à envoyer.
            format_type (str): Format d'envoi ('text' ou 'hex').
        """
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
                # Utiliser le format défini dans les paramètres
                format_type = send_settings.get('format', 'ASCII').lower()
                if format_type == 'ascii':
                    format_type = 'text'
                elif format_type == 'hex':
                    format_type = 'hex'
                
                # Ajouter la fin de ligne si définie
                eol = send_settings.get('eol', 'Aucun')
                if eol == 'NL':
                    data += '\n'
                elif eol == 'CR':
                    data += '\r'
                elif eol == 'NL+CR':
                    data += '\r\n'
            
            # Convertir les données selon le format
            if format_type == 'hex':
                # Traitement hexadécimal
                try:
                    # Nettoyer la chaîne hex et la convertir en bytes
                    hex_data = data.replace(' ', '').replace('0x', '')
                    data_bytes = bytes.fromhex(hex_data)
                except ValueError:
                    self.append_text("Format hexadécimal invalide\n", 'error')
                    return
            else:
                # Format texte/ASCII
                data_bytes = data.encode('utf-8')
            
            success = self.serial_manager.send_data(data_bytes)
            if success:
                # Mettre à jour le compteur d'octets envoyés
                self.update_bytes_counter(sent=len(data_bytes))
                
                # Afficher les données envoyées avec le format de l'original (TX:)
                timestamp = ""
                if self.advanced_panel.display_group.isChecked():
                    display_settings = self.advanced_panel.get_display_settings()
                    if display_settings.get('timestamp', False):
                        from datetime import datetime
                        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] "
                
                display_data = data if format_type == 'text' else f"[{format_type.upper()}] {data}"
                self.append_text(f"{timestamp}TX: {display_data}\n", 'sent')
                
                # Effacer le champ d'entrée après envoi
                self.input_panel.clear_input()
            else:
                self.append_text("Échec de l'envoi des données\n", 'error')
        except Exception as e:
            self.append_text(f"Erreur d'envoi: {str(e)}\n", 'error')
            logger.error(f"Erreur d'envoi de données: {str(e)}")
    
    # Correction des signatures et docstrings pour les dernières méthodes publiques
    def on_data_received(self, data: bytes) -> None:
        """
        Traite les données reçues du port série.
        Args:
            data (bytes): Données reçues.
        Returns:
            None
        """
        try:
            # Décodage des données
            text: str = data.decode('utf-8', errors='replace')

            # Nettoyage complet du texte
            clean_text: str = self.clean_received_text(text)

            # Afficher le texte reçu directement sans préfixe, comme dans l'original
            self.append_text(clean_text, 'received')

            # Mise à jour des statistiques
            self.update_bytes_counter(received=len(data))
        except Exception as e:
            logger.error(f"Erreur de traitement des données reçues: {str(e)}")
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
        # Supprimer les séquences d'échappement ANSI (comme \x1b[...)
        text = re.sub(r'\x1b\[[0-9;]*[mK]', '', text)
        
        return text

    def on_connection_changed(self, connected: bool) -> None:
        """
        Traite le changement d'état de connexion série.
        Args:
            connected (bool): État de connexion.
        Returns:
            None
        """
        try:
            if connected:
                self.connection_status_label.setText("Connecté")
                self.connection_status_label.setStyleSheet("color: green;")
                port = self.serial_panel.get_connection_params()['port']
                self.port_label.setText(f"Port: {port}")
                # Mettre à jour le bouton dans le panneau série
                self.serial_panel.set_connected(True)
            else:
                self.connection_status_label.setText("Déconnecté")
                self.connection_status_label.setStyleSheet("color: red;")
                self.port_label.setText("Aucun port")
                # Mettre à jour le bouton dans le panneau série
                self.serial_panel.set_connected(False)
                # Rafraîchir la liste des ports en cas de déconnexion
                self.refresh_ports()
                
            logger.info(f"État de connexion mis à jour: {'Connecté' if connected else 'Déconnecté'}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'état de connexion: {e}")

    def on_error_occurred(self, error_message: str) -> None:
        """
        Traite les erreurs du gestionnaire série.
        Args:
            error_message (str): Message d'erreur.
        Returns:
            None
        """
        self.append_text(f"[Erreur] {error_message}\n", 'error')
        logger.error(f"Erreur série: {error_message}")

    def on_statistics_updated(self, stats: Dict[str, Any]) -> None:
        """
        Met à jour les statistiques affichées dans l'interface.
        Args:
            stats (Dict[str, Any]): Dictionnaire contenant les statistiques à afficher.
        Returns:
            None
        """
        try:
            rx_bytes: int = int(stats.get('rx_bytes', 0))
            tx_bytes: int = int(stats.get('tx_bytes', 0))
            uptime: int = int(stats.get('uptime', 0))
            
            # Synchroniser nos compteurs locaux avec ceux du gestionnaire
            self.rx_bytes_count = rx_bytes
            self.tx_bytes_count = tx_bytes
            
            # Mettre à jour l'affichage
            uptime_str = f"{int(uptime//3600):02d}:{int((uptime%3600)//60):02d}:{int(uptime%60):02d}"
            
            self.bytes_label.setText(f"Octets: {tx_bytes} ↑ / {rx_bytes} ↓ | Durée: {uptime_str}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des statistiques : {str(e)}")
            raise

    def refresh_ports(self) -> None:
        """
        Rafraîchit la liste des ports série disponibles.
        Returns:
            None
        """
        try:
            ports = self.serial_manager.get_available_ports()
            self.serial_panel.update_ports(ports)
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement des ports: {str(e)}")

    def clear_terminal(self) -> None:
        """
        Efface le contenu du terminal et optimise la mémoire.
        Returns:
            None
        """
        if self.terminal_output:
            try:
                # 1. Arrêter temporairement le timer de flush
                if hasattr(self, '_update_timer') and self._update_timer.isActive():
                    self._update_timer.stop()
                
                # 2. Vider complètement le buffer sans traitement
                if hasattr(self, '_pending_text_buffer'):
                    self._pending_text_buffer.clear()
                
                # 3. Nettoyage ultra-complet du document
                doc = self.terminal_output.document()
                doc.clear()  # Plus efficace que terminal_output.clear()
                
                # 4. Réinitialiser le pool de curseurs
                self._cursor_pool = None
                self._last_cursor_position = 0
                
                # 5. Nettoyer complètement le cache de formats
                if hasattr(self, '_text_format_cache'):
                    self._text_format_cache.clear()
                
                # 6. Reset compteur d'objets
                self._object_creation_count = 0
                
                # 7. Forcer garbage collection intensif
                import gc
                for _ in range(3):
                    gc.collect()
                
                # 8. Redémarrer le timer
                if hasattr(self, '_update_timer'):
                    self._update_timer.start(100)
                
                # 9. Ajouter le message de nettoyage (en direct, pas de batching)
                cursor = self.terminal_output.textCursor()
                cursor.movePosition(QTextCursor.End)
                format_obj = self._get_cached_format('system')
                cursor.setCharFormat(format_obj)
                cursor.insertText("[Système] Terminal effacé - Mémoire optimisée\n")
                
                logger.debug("Nettoyage mémoire ultra-complet effectué")
                
            except Exception as e:
                logger.error(f"Erreur nettoyage ultra-complet: {e}")
                # Fallback: nettoyage basique
                try:
                    self.terminal_output.clear()
                    if hasattr(self, '_text_format_cache'):
                        self._text_format_cache.clear()
                    if hasattr(self, '_pending_text_buffer'):
                        self._pending_text_buffer.clear()
                except:
                    pass
    
    def _direct_append_text(self, text: str, color: str = 'text') -> None:
        """
        Ajoute du texte directement dans le terminal sans buffer.
        Args:
            text (str): Texte à ajouter.
            color (str): Couleur à utiliser.
        Returns:
            None
        """
        if not self.terminal_output:
            return
        try:
            cursor = self.terminal_output.textCursor()
            cursor.movePosition(QTextCursor.End)
            # Appliquer la couleur
            if hasattr(self, '_text_format_cache') and color in self._text_format_cache:
                cursor.setCharFormat(self._text_format_cache[color])
            cursor.insertText(text)
            self.terminal_output.setTextCursor(cursor)
            self.terminal_output.ensureCursorVisible()
        except Exception as e:
            logger.error(f"Erreur dans _direct_append_text: {e}")

    def _flush_text_buffer(self) -> None:
        """
        Flush le buffer de texte avec gestion mémoire ultra-optimisée.
        Returns:
            None
        """
        if not self._pending_text_buffer or not self.terminal_output:
            return
        try:
            # Surveillance proactive de la mémoire
            self._monitor_memory_usage()
            # Utilisation d'un curseur réutilisable
            if not self._cursor_pool:
                self._cursor_pool = self.terminal_output.textCursor()
            cursor = self._cursor_pool
            cursor.movePosition(QTextCursor.End)
            # Optimisation: une seule transaction pour tout le batch
            cursor.beginEditBlock()
            try:
                # Traitement ultra-optimisé
                current_format = None
                for text, color in self._pending_text_buffer:
                    # Optimisation: ne changer le format que si nécessaire
                    new_format = self._get_cached_format(color)
                    if new_format != current_format:
                        cursor.setCharFormat(new_format)
                        current_format = new_format
                    cursor.insertText(text)
                    self._object_creation_count += 1
            finally:
                cursor.endEditBlock()
            # Mise à jour du curseur position (optimisation)
            self._last_cursor_position = cursor.position()
            self.terminal_output.setTextCursor(cursor)
            self.terminal_output.ensureCursorVisible()
            # Nettoyage du buffer
            self._pending_text_buffer.clear()
        except Exception as e:
            logger.error(f"Erreur dans flush_text_buffer optimisé: {e}")
            self._pending_text_buffer.clear()

    def _monitor_memory_usage(self) -> None:
        """
        Surveillance et nettoyage proactif de la mémoire.
        Returns:
            None
        """
        try:
            # Vérifier la taille du document
            if self.terminal_output:
                doc = self.terminal_output.document()
                char_count = doc.characterCount()
                # Nettoyage agressif si nécessaire
                if char_count > self._max_terminal_chars * self._cleanup_threshold:
                    self._aggressive_cleanup()
                # Nettoyage du cache si trop gros
                if len(self._text_format_cache) > 10:
                    self._cleanup_format_cache()
        except Exception as e:
            logger.debug(f"Erreur monitoring mémoire: {e}")

    def _aggressive_cleanup(self) -> None:
        """
        Nettoyage agressif pour libérer la mémoire.
        Returns:
            None
        """
        try:
            if not self.terminal_output:
                return
            # Sauvegarder seulement les dernières lignes importantes
            doc = self.terminal_output.document()
            total_blocks = doc.blockCount()
            if total_blocks > 200:  # Très agressif
                # Supprimer tout et garder seulement un message
                self.terminal_output.clear()
                # Nettoyer le cache
                self._text_format_cache.clear()
                self._cursor_pool = None
                # Message de nettoyage
                self._add_single_text("[Système] Nettoyage mémoire automatique effectué\n", 'system')
                # Forcer garbage collection
                import gc
                gc.collect()
                logger.debug("Nettoyage agressif effectué")
        except Exception as e:
            logger.error(f"Erreur nettoyage agressif: {e}")

    def _cleanup_format_cache(self) -> None:
        """
        Nettoie le cache de formats en gardant seulement les essentiels.
        Returns:
            None
        """
        try:
            # Garder seulement les formats du thème actuel
            current_theme_keys = [k for k in self._text_format_cache.keys() 
                                if k.startswith(f"{self.current_theme}_")]
            # Nettoyer les anciens formats
            self._text_format_cache = {k: v for k, v in self._text_format_cache.items() 
                                     if k in current_theme_keys[:5]}  # Max 5 formats
            logger.debug(f"Cache formats nettoyé: {len(self._text_format_cache)} formats restants")
        except Exception as e:
            logger.debug(f"Erreur nettoyage cache: {e}")

    def _get_cached_format(self, color: str) -> QTextCharFormat:
        """
        Obtient un format depuis le cache ou le crée.
        Args:
            color (str): Couleur à utiliser.
        Returns:
            QTextCharFormat: Format de texte PyQt5.
        """
        cache_key = f"{self.current_theme}_{color}"
        if cache_key not in self._text_format_cache:
            format_obj = QTextCharFormat()
            # Couleur unique selon le thème actuel
            if self.current_theme == 'hacker':
                format_obj.setForeground(QColor(0, 255, 0))  # Vert
            elif self.current_theme == 'clair':
                format_obj.setForeground(QColor(0, 0, 0))    # Noir
            else:  # sombre ou par défaut
                format_obj.setForeground(QColor(255, 255, 255))  # Blanc
            self._text_format_cache[cache_key] = format_obj
        return self._text_format_cache[cache_key]

    def _add_single_text(self, text: str, color: str = 'text') -> None:
        """
        Ajoute un texte unique immédiatement sans batching.
        Args:
            text (str): Texte à ajouter.
            color (str): Couleur à utiliser.
        Returns:
            None
        """
        if not self.terminal_output:
            return
        cursor = self.terminal_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        format_obj = self._get_cached_format(color)
        cursor.setCharFormat(format_obj)
        cursor.insertText(text)
        self.terminal_output.setTextCursor(cursor)
        self.terminal_output.ensureCursorVisible()

    def append_text(self, text: str, color: str = 'text') -> None:
        """
        Ajoute du texte coloré au terminal avec gestionnaire mémoire ultra.
        Args:
            text (str): Texte à ajouter.
            color (str): Couleur à utiliser.
        Returns:
            None
        """
        try:
            # Utiliser le gestionnaire mémoire ultra pour le batching
            # Le gestionnaire ultra ne supporte que le texte simple, donc on formatera après
            should_flush = self.ultra_memory.add_to_buffer(text)
            # Stocker la couleur pour le flush
            if not hasattr(self, '_color_buffer'):
                self._color_buffer = []
            self._color_buffer.append(color)
            # Auto-flush si le buffer devient trop grand ou si demandé
            if should_flush:
                self._ultra_flush_buffer()
        except Exception as e:
            # Fallback: ajout direct si problème avec le gestionnaire mémoire
            self._direct_append_text(text, color)
    
    def select_font(self) -> None:
        """
        Ouvre le dialogue de sélection de police.
        Returns:
            None
        """
        font, ok = QFontDialog.getFont(self.terminal_output.font(), self)
        if ok:
            self.terminal_output.setFont(font)
            # Sauvegarder la police sélectionnée
            self.settings_manager.save_setting('terminal_font', font.toString())
            logger.info(f"Police changée: {font.family()} {font.pointSize()}pt")

    def show_checksum_calculator(self) -> None:
        """
        Affiche le calculateur de checksum.
        Returns:
            None
        """
        self.checksum_calculator.show()

    def show_data_converter(self) -> None:
        """
        Affiche le convertisseur de données.
        Returns:
            None
        """
        self.data_converter.show()

    def update_bytes_counter(self, sent: int = 0, received: int = 0) -> None:
        """
        Met à jour le compteur d'octets de manière cumulative.
        Args:
            sent (int): Octets envoyés à ajouter.
            received (int): Octets reçus à ajouter.
        Returns:
            None
        """
        try:
            self.tx_bytes_count += sent
            self.rx_bytes_count += received
            self.bytes_label.setText(f"Octets: {self.tx_bytes_count} ↑ / {self.rx_bytes_count} ↓")
        except Exception as e:
            logger.error(f"Erreur mise à jour compteur: {str(e)}")
    
    def load_settings(self) -> None:
        """
        Charge les paramètres sauvegardés.
        Returns:
            None
        """
        try:
            settings = self.settings_manager.load_all_settings()
            if settings:
                # Appliquer le thème
                theme = settings.get('theme', 'sombre')
                if theme in ['clair', 'sombre', 'hacker']:
                    self.change_theme(theme)
                
                # Restaurer la géométrie de la fenêtre
                if 'window_geometry' in settings:
                    self.restoreGeometry(settings['window_geometry'])
                
                # Restaurer la police du terminal
                if 'terminal_font' in settings:
                    font = QFont()
                    font.fromString(settings['terminal_font'])
                    self.terminal_output.setFont(font)
                
                # Restaurer la visibilité de l'onglet des paramètres
                settings_tab_visible = settings.get('settings_tab_visible', False)  # Défaut : masqué
                # Convertir en booléen si c'est une chaîne (problème de sérialisation QSettings)
                if isinstance(settings_tab_visible, str):
                    settings_tab_visible = settings_tab_visible.lower() == 'true'
                
                logger.debug(f"Chargement paramètres - settings_tab_visible: {settings_tab_visible} (type: {type(settings_tab_visible)})")
                self.settings_tab_visible = settings_tab_visible
                
                if settings_tab_visible:
                    # Ajouter l'onglet des paramètres s'il doit être visible
                    self.settings_tab_index = self.tab_widget.addTab(self.advanced_panel, "⚙️ Paramètres")
                    self.toggle_settings_tab_action.setChecked(True)
                    self.toggle_settings_tab_action.setText('Masquer l\'onglet paramètres')
                else:
                    # L'onglet reste masqué
                    self.toggle_settings_tab_action.setChecked(False)
                    self.toggle_settings_tab_action.setText('Afficher l\'onglet paramètres')
                
                # Restaurer la visibilité du panneau d'envoi
                send_panel_visible = settings.get('send_panel_visible', True)  # Défaut : visible
                # Convertir en booléen si c'est une chaîne (problème de sérialisation QSettings)
                if isinstance(send_panel_visible, str):
                    send_panel_visible = send_panel_visible.lower() == 'true'
                
                self.input_panel.setVisible(send_panel_visible)
                
                if send_panel_visible:
                    self.toggle_send_panel_action.setChecked(True)
                    self.toggle_send_panel_action.setText('Masquer le panneau d\'envoi')
                else:
                    self.toggle_send_panel_action.setChecked(False)
                    self.toggle_send_panel_action.setText('Afficher le panneau d\'envoi')
                
                logger.info("Paramètres chargés avec succès")
            else:
                # Première utilisation - valeurs par défaut
                self.settings_tab_visible = False
                self.toggle_settings_tab_action.setChecked(False)
                self.toggle_settings_tab_action.setText('Afficher l\'onglet paramètres')
                
                # Panneau d'envoi visible par défaut
                if self.input_panel:
                    self.input_panel.setVisible(True)
                    self.toggle_send_panel_action.setChecked(True)
                    self.toggle_send_panel_action.setText('Masquer le panneau d\'envoi')
                
                logger.info("Première utilisation - paramètres par défaut appliqués")
                    
        except Exception as e:
            logger.error(f"Erreur lors du chargement des paramètres: {str(e)}")
            # Appliquer le thème par défaut en cas d'erreur
            self.change_theme('sombre')
            # État par défaut en cas d'erreur
            if not hasattr(self, 'settings_tab_visible'):
                self.settings_tab_visible = False
                self.toggle_settings_tab_action.setChecked(False)
                self.toggle_settings_tab_action.setText('Afficher l\'onglet paramètres')
            
            # Panneau d'envoi visible par défaut en cas d'erreur
            if self.input_panel:
                self.input_panel.setVisible(True)
                self.toggle_send_panel_action.setChecked(True)
                self.toggle_send_panel_action.setText('Masquer le panneau d\'envoi')
    
    def save_settings(self) -> None:
        """
        Sauvegarde les paramètres actuels.
        Returns:
            None
        """
        try:
            settings = {
                'window_geometry': self.saveGeometry(),
                'terminal_font': self.terminal_output.font().toString(),
                'theme': getattr(self, 'current_theme', 'sombre'),
                'settings_tab_visible': getattr(self, 'settings_tab_visible', False),
                'send_panel_visible': self.input_panel.isVisible() if self.input_panel else True
            }
            logger.debug(f"Sauvegarde paramètres - settings_tab_visible: {settings['settings_tab_visible']} (type: {type(settings['settings_tab_visible'])})")
            self.settings_manager.save_all_settings(settings)
            logger.info("Paramètres sauvegardés avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des paramètres: {str(e)}")
    
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
        Change le thème de l'application.
        Args:
            theme_name (str): Nom du thème à appliquer.
        Returns:
            None
        """
        try:
            from interface.theme_manager import apply_theme
            apply_theme(theme_name)
            self.current_theme = theme_name
            # Appliquer les couleurs du terminal
            self.apply_terminal_colors()
            # Forcer la mise à jour visuelle du terminal
            self.refresh_terminal_display()
            logger.info(f"Thème changé: {theme_name}")
        except Exception as e:
            logger.error(f"Erreur lors du changement de thème: {e}")

    def refresh_terminal_display(self) -> None:
        """
        Force la mise à jour visuelle du terminal avec les nouvelles couleurs.
        Returns:
            None
        """
        try:
            # Sauvegarder le contenu actuel
            current_content = self.terminal_output.toPlainText()
            if current_content:
                # Effacer et réécrire le contenu pour appliquer les nouvelles couleurs
                self.terminal_output.clear()
                # Ajouter un message de changement de thème
                self.append_text(f"[Système] Thème changé vers '{self.current_theme}'\n", 'system')
                # Note: Le contenu précédent est perdu mais c'est acceptable pour un changement de thème
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du terminal: {e}")

    def apply_terminal_colors(self) -> None:
        """
        Applique les couleurs du terminal selon le thème actuel.
        Returns:
            None
        """
        try:
            if self.terminal_output:
                # Définir les couleurs selon le thème
                if self.current_theme == 'hacker':
                    text_color = "#00ff00"  # Vert
                    bg_color = "#000000"    # Noir
                elif self.current_theme == 'clair':
                    text_color = "#000000"  # Noir
                    bg_color = "#ffffff"    # Blanc
                else:  # sombre ou par défaut
                    text_color = "#ffffff"  # Blanc
                    bg_color = "#2a2a2a"    # Gris sombre
                style = f"""
                    QTextEdit {{
                        background-color: {bg_color};
                        color: {text_color};
                        border: 1px solid #555;
                        font-family: 'Consolas', 'Courier New', monospace;
                    }}
                """
                self.terminal_output.setStyleSheet(style)
                logger.debug(f"Couleurs appliquées pour thème '{self.current_theme}': texte={text_color}, fond={bg_color}")
            else:
                logger.warning("terminal_output non initialisé")
        except Exception as e:
            logger.error(f"Erreur lors de l'application des couleurs: {e}")

    def change_font(self) -> None:
        """
        Ouvre un dialogue pour changer la police du terminal.
        Returns:
            None
        """
        try:
            current_font = self.terminal_output.font() if self.terminal_output else QFont("Consolas", 10)
            font, ok = QFontDialog.getFont(current_font, self, "Choisir la police du terminal")
            if ok and self.terminal_output:
                self.terminal_output.setFont(font)
                logger.info(f"Police changée: {font.family()}, taille: {font.pointSize()}")
        except Exception as e:
            logger.error(f"Erreur lors du changement de police: {str(e)}")

    def toggle_send_panel_visibility(self) -> None:
        """
        Masque ou affiche le panneau d'envoi.
        Returns:
            None
        """
        try:
            is_visible = self.input_panel.isVisible()
            self.input_panel.setVisible(not is_visible)
            # Mettre à jour le texte de l'action
            if is_visible:
                self.toggle_send_panel_action.setText('Afficher le panneau d\'envoi')
            else:
                self.toggle_send_panel_action.setText('Masquer le panneau d\'envoi')
            # Sauvegarder les paramètres
            self.save_settings()
            logger.info(f"Panneau d'envoi {'masqué' if is_visible else 'affiché'}")
        except Exception as e:
            logger.error(f"Erreur lors du basculement du panneau d'envoi: {str(e)}")

    def toggle_settings_tab_visibility(self) -> None:
        """
        Masque ou affiche l'onglet des paramètres.
        Returns:
            None
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

    def setupShortcuts(self) -> None:
        """
        Configure les raccourcis clavier.
        Returns:
            None
        """
        # Cette méthode est appelée dans __init__ mais n'était pas définie
        pass

    def reset_config(self) -> None:
        """
        Réinitialise l'apparence au thème par défaut.
        Returns:
            None
        """
        try:
            self.change_theme('sombre')
            if self.terminal_output:
                self.terminal_output.setFont(QFont("Consolas", 10))
            logger.info("Configuration réinitialisée au thème sombre")
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation: {str(e)}")

    def apply_theme(self, theme_name: str) -> None:
        """
        Applique un thème à l'application.
        Args:
            theme_name (str): Nom du thème à appliquer.
        Returns:
            None
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

__all__ = []
