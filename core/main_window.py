"""
Main Window Module pour CrazyTerm.

Ce module implémente la fenêtre principale de l'application CrazyTerm,
avec une architecture robuste, performante et bien documentée.

Fonctionnalités:
    - Interface utilisateur principale avec PyQt5/PySide2
    - Gestion des communications série
    - Système de logging avancé
    - Gestion d'erreurs robuste
    - Optimisations de performance
    - Architecture thread-safe

Auteur: CrazyTerm Development Team
Version: 1.0.0
License: MIT
"""

import sys
import logging
import asyncio
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from contextlib import contextmanager
from datetime import datetime, timezone

try:
    from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                                 QTextEdit, QLineEdit, QPushButton, QLabel, 
                                 QComboBox, QSpinBox, QCheckBox, QGroupBox,
                                 QMenuBar, QStatusBar, QMessageBox, QSplitter,
                                 QTabWidget, QProgressBar, QGridLayout)
    from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal, QObject
    from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
    PYQT_AVAILABLE = True
except ImportError:
    try:
        from PySide2.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                       QTextEdit, QLineEdit, QPushButton, QLabel,
                                       QComboBox, QSpinBox, QCheckBox, QGroupBox,
                                       QMenuBar, QStatusBar, QMessageBox, QSplitter,
                                       QTabWidget, QProgressBar, QGridLayout)
        from PySide2.QtCore import Qt, QThread, QTimer, Signal as pyqtSignal, QObject
        from PySide2.QtGui import QFont, QIcon, QPalette, QColor
        PYQT_AVAILABLE = True
    except ImportError:
        PYQT_AVAILABLE = False

# Imports locaux
from .config_manager import ConfigManager
from .ui_manager import UIManager
from .tool_manager import ToolManager
from .terminal_display import TerminalDisplay
from ..communication.serial_communication import SerialCommunication
from ..interface.theme_manager import ThemeManager
from ..system.error_handling import ErrorHandler
from ..system.memory_optimizer import MemoryOptimizer
from ..system.utilities import Utilities


@dataclass
class MainWindowConfig:
    """Configuration pour la fenêtre principale."""
    
    title: str = "CrazyTerm - Terminal Série Avancé"
    width: int = 1200
    height: int = 800
    min_width: int = 800
    min_height: int = 600
    auto_connect: bool = False
    remember_geometry: bool = True
    theme: str = "dark"
    log_level: str = "INFO"
    
    # Performance
    max_lines: int = 10000
    refresh_rate: int = 60
    buffer_size: int = 8192
    
    # Sécurité
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = field(default_factory=lambda: ['.txt', '.log', '.csv'])


class MainWindow(QMainWindow):
    """
    Fenêtre principale de l'application CrazyTerm.
    
    Cette classe implémente l'interface utilisateur principale avec une architecture
    robuste, thread-safe et optimisée pour les performances.
    
    Attributes:
        config (MainWindowConfig): Configuration de la fenêtre
        logger (logging.Logger): Logger pour les opérations
        error_handler (ErrorHandler): Gestionnaire d'erreurs
        memory_optimizer (MemoryOptimizer): Optimiseur de mémoire
        
    Signals:
        connection_changed (bool): Émis quand l'état de connexion change
        data_received (str): Émis quand des données sont reçues
        error_occurred (str): Émis quand une erreur se produit
        
    Methods:
        __init__: Initialise la fenêtre principale
        setup_ui: Configure l'interface utilisateur
        setup_connections: Configure les connexions série
        connect_serial: Établit une connexion série
        disconnect_serial: Ferme la connexion série
        send_data: Envoie des données via la connexion série
        receive_data: Traite les données reçues
        
    Examples:
        >>> window = MainWindow()
        >>> window.show()
        >>> window.connect_serial("COM1", 9600)
        
    Note:
        Cette classe est thread-safe et optimisée pour les performances.
        Elle gère automatiquement la mémoire et les erreurs.
    """
    
    # Signaux Qt
    connection_changed = pyqtSignal(bool)
    data_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config: Optional[MainWindowConfig] = None) -> None:
        """
        Initialise la fenêtre principale.
        
        Args:
            config: Configuration optionnelle pour la fenêtre
            
        Raises:
            RuntimeError: Si Qt n'est pas disponible
            ValueError: Si la configuration est invalide
        """
        super().__init__()
        
        # Vérifier Qt
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 ou PySide2 requis pour l'interface graphique")
        
        # Configuration
        self.config = config or MainWindowConfig()
        
        # Initialisation des composants
        self._init_logging()
        self._init_error_handling()
        self._init_memory_management()
        self._init_components()
        
        # État interne
        self._is_connected = False
        self._connection_lock = threading.Lock()
        self._data_buffer = []
        self._performance_metrics = {}
        
        # Configuration de l'interface
        self.setup_ui()
        self.setup_connections()
        
        # Logging
        self.logger.info("MainWindow initialisée avec succès")
    
    def _init_logging(self) -> None:
        """Initialise le système de logging."""
        self.logger = logging.getLogger(f"{__name__}.MainWindow")
        self.logger.setLevel(getattr(logging, self.config.log_level, logging.INFO))
        
        # Configuration du handler si nécessaire
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _init_error_handling(self) -> None:
        """Initialise le gestionnaire d'erreurs."""
        try:
            self.error_handler = ErrorHandler()
        except Exception as e:
            self.logger.warning(f"Impossible d'initialiser ErrorHandler: {e}")
            self.error_handler = None
    
    def _init_memory_management(self) -> None:
        """Initialise l'optimiseur de mémoire."""
        try:
            self.memory_optimizer = MemoryOptimizer()
        except Exception as e:
            self.logger.warning(f"Impossible d'initialiser MemoryOptimizer: {e}")
            self.memory_optimizer = None
    
    def _init_components(self) -> None:
        """Initialise les composants principaux."""
        try:
            self.config_manager = ConfigManager()
            self.ui_manager = UIManager(self)
            self.tool_manager = ToolManager(self)
            self.terminal_display = TerminalDisplay(self)
            self.serial_communication = SerialCommunication()
            self.theme_manager = ThemeManager(self)
            
            self.logger.info("Composants initialisés avec succès")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation des composants: {e}")
            if self.error_handler:
                self.error_handler.handle_error(e)
            raise
    
    def setup_ui(self) -> None:
        """
        Configure l'interface utilisateur.
        
        Raises:
            RuntimeError: Si l'UI ne peut pas être configurée
        """
        try:
            # Configuration de la fenêtre
            self.setWindowTitle(self.config.title)
            self.setMinimumSize(self.config.min_width, self.config.min_height)
            self.resize(self.config.width, self.config.height)
            
            # Widget central
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Layout principal
            main_layout = QVBoxLayout(central_widget)
            
            # Barre d'outils
            self._setup_toolbar()
            
            # Zone de terminal
            self._setup_terminal_area(main_layout)
            
            # Zone de contrôles
            self._setup_controls_area(main_layout)
            
            # Barre de statut
            self._setup_status_bar()
            
            # Appliquer le thème
            self.theme_manager.apply_theme(self.config.theme)
            
            self.logger.info("Interface utilisateur configurée")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la configuration de l'UI: {e}")
            if self.error_handler:
                self.error_handler.handle_error(e)
            raise RuntimeError(f"Impossible de configurer l'interface: {e}")
    
    def _setup_toolbar(self) -> None:
        """Configure la barre d'outils."""
        toolbar = self.addToolBar("Outils")
        
        # Bouton connexion/déconnexion
        self.connect_button = QPushButton("Connecter")
        self.connect_button.clicked.connect(self.toggle_connection)
        toolbar.addWidget(self.connect_button)
        
        toolbar.addSeparator()
        
        # Bouton effacer
        clear_button = QPushButton("Effacer")
        clear_button.clicked.connect(self.clear_terminal)
        toolbar.addWidget(clear_button)
        
        # Bouton sauvegarder
        save_button = QPushButton("Sauvegarder")
        save_button.clicked.connect(self.save_log)
        toolbar.addWidget(save_button)
    
    def _setup_terminal_area(self, layout: QVBoxLayout) -> None:
        """Configure la zone de terminal."""
        terminal_group = QGroupBox("Terminal")
        terminal_layout = QVBoxLayout(terminal_group)
        
        # Zone d'affichage
        self.terminal_display_widget = QTextEdit()
        self.terminal_display_widget.setReadOnly(True)
        self.terminal_display_widget.setFont(QFont("Consolas", 10))
        terminal_layout.addWidget(self.terminal_display_widget)
        
        # Zone de saisie
        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Tapez votre commande ici...")
        self.input_line.returnPressed.connect(self.send_command)
        
        send_button = QPushButton("Envoyer")
        send_button.clicked.connect(self.send_command)
        
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(send_button)
        terminal_layout.addLayout(input_layout)
        
        layout.addWidget(terminal_group)
    
    def _setup_controls_area(self, layout: QVBoxLayout) -> None:
        """Configure la zone de contrôles."""
        controls_group = QGroupBox("Contrôles")
        controls_layout = QHBoxLayout(controls_group)
        
        # Configuration série
        serial_group = QGroupBox("Configuration Série")
        serial_layout = QGridLayout(serial_group)
        
        # Port
        serial_layout.addWidget(QLabel("Port:"), 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        serial_layout.addWidget(self.port_combo, 0, 1)
        
        # Vitesse
        serial_layout.addWidget(QLabel("Vitesse:"), 1, 0)
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.speed_combo.setCurrentText("9600")
        serial_layout.addWidget(self.speed_combo, 1, 1)
        
        # Bits de données
        serial_layout.addWidget(QLabel("Bits:"), 2, 0)
        self.data_bits_combo = QComboBox()
        self.data_bits_combo.addItems(["7", "8"])
        self.data_bits_combo.setCurrentText("8")
        serial_layout.addWidget(self.data_bits_combo, 2, 1)
        
        # Parité
        serial_layout.addWidget(QLabel("Parité:"), 3, 0)
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["None", "Even", "Odd"])
        serial_layout.addWidget(self.parity_combo, 3, 1)
        
        controls_layout.addWidget(serial_group)
        
        # Outils
        tools_group = QGroupBox("Outils")
        tools_layout = QVBoxLayout(tools_group)
        
        calc_button = QPushButton("Calculatrice")
        calc_button.clicked.connect(self.open_calculator)
        tools_layout.addWidget(calc_button)
        
        checksum_button = QPushButton("Checksum")
        checksum_button.clicked.connect(self.open_checksum)
        tools_layout.addWidget(checksum_button)
        
        converter_button = QPushButton("Convertisseur")
        converter_button.clicked.connect(self.open_converter)
        tools_layout.addWidget(converter_button)
        
        controls_layout.addWidget(tools_group)
        
        layout.addWidget(controls_group)
    
    def _setup_status_bar(self) -> None:
        """Configure la barre de statut."""
        self.status_bar = self.statusBar()
        
        # Statut de connexion
        self.connection_status = QLabel("Déconnecté")
        self.status_bar.addWidget(self.connection_status)
        
        # Compteur de données
        self.data_counter = QLabel("0 octets")
        self.status_bar.addPermanentWidget(self.data_counter)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def setup_connections(self) -> None:
        """Configure les connexions de signaux."""
        try:
            # Connexions internes
            self.connection_changed.connect(self.on_connection_changed)
            self.data_received.connect(self.on_data_received)
            self.error_occurred.connect(self.on_error_occurred)
            
            # Connexions avec les composants
            if hasattr(self.serial_communication, 'data_received'):
                self.serial_communication.data_received.connect(self.data_received)
            
            if hasattr(self.serial_communication, 'error_occurred'):
                self.serial_communication.error_occurred.connect(self.error_occurred)
            
            # Timer pour les mises à jour
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_display)
            self.update_timer.start(1000 // self.config.refresh_rate)
            
            # Timer pour l'optimisation mémoire
            if self.memory_optimizer:
                self.memory_timer = QTimer()
                self.memory_timer.timeout.connect(self.optimize_memory)
                self.memory_timer.start(30000)  # 30 secondes
            
            self.logger.info("Connexions configurées")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la configuration des connexions: {e}")
            if self.error_handler:
                self.error_handler.handle_error(e)
    
    def toggle_connection(self) -> None:
        """Bascule l'état de la connexion série."""
        try:
            if self._is_connected:
                self.disconnect_serial()
            else:
                self.connect_serial()
        except Exception as e:
            self.logger.error(f"Erreur lors du basculement de connexion: {e}")
            self.error_occurred.emit(str(e))
    
    def connect_serial(self) -> bool:
        """
        Établit une connexion série.
        
        Returns:
            bool: True si la connexion a réussi, False sinon
        """
        try:
            with self._connection_lock:
                if self._is_connected:
                    self.logger.warning("Déjà connecté")
                    return True
                
                # Paramètres de connexion
                port = self.port_combo.currentText()
                baudrate = int(self.speed_combo.currentText())
                
                # Établir la connexion
                success = self.serial_communication.connect(
                    port=port,
                    baudrate=baudrate,
                    databits=int(self.data_bits_combo.currentText()),
                    parity=self.parity_combo.currentText(),
                    timeout=1.0
                )
                
                if success:
                    self._is_connected = True
                    self.connection_changed.emit(True)
                    self.logger.info(f"Connexion établie sur {port} à {baudrate} bauds")
                    return True
                else:
                    self.logger.error("Impossible d'établir la connexion")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Erreur lors de la connexion: {e}")
            self.error_occurred.emit(str(e))
            return False
    
    def disconnect_serial(self) -> bool:
        """
        Ferme la connexion série.
        
        Returns:
            bool: True si la déconnexion a réussi, False sinon
        """
        try:
            with self._connection_lock:
                if not self._is_connected:
                    self.logger.warning("Déjà déconnecté")
                    return True
                
                # Fermer la connexion
                success = self.serial_communication.disconnect()
                
                if success:
                    self._is_connected = False
                    self.connection_changed.emit(False)
                    self.logger.info("Connexion fermée")
                    return True
                else:
                    self.logger.error("Erreur lors de la déconnexion")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Erreur lors de la déconnexion: {e}")
            self.error_occurred.emit(str(e))
            return False
    
    def send_command(self) -> None:
        """Envoie une commande via la connexion série."""
        try:
            if not self._is_connected:
                self.logger.warning("Pas de connexion active")
                return
            
            command = self.input_line.text().strip()
            if not command:
                return
            
            # Envoyer la commande
            success = self.serial_communication.send_data(command + '\r\n')
            
            if success:
                # Afficher la commande envoyée
                self.terminal_display_widget.append(f"> {command}")
                self.input_line.clear()
                self.logger.debug(f"Commande envoyée: {command}")
            else:
                self.logger.error("Erreur lors de l'envoi de la commande")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de commande: {e}")
            self.error_occurred.emit(str(e))
    
    def clear_terminal(self) -> None:
        """Efface le contenu du terminal."""
        try:
            self.terminal_display_widget.clear()
            self._data_buffer.clear()
            self.logger.info("Terminal effacé")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'effacement: {e}")
    
    def save_log(self) -> None:
        """Sauvegarde le contenu du terminal."""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Sauvegarder le log",
                f"crazyterm_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Fichiers texte (*.txt);;Tous les fichiers (*)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.terminal_display_widget.toPlainText())
                
                self.logger.info(f"Log sauvegardé: {filename}")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {e}")
            self.error_occurred.emit(str(e))
    
    def open_calculator(self) -> None:
        """Ouvre la calculatrice."""
        try:
            self.tool_manager.open_calculator()
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ouverture de la calculatrice: {e}")
    
    def open_checksum(self) -> None:
        """Ouvre l'outil de checksum."""
        try:
            self.tool_manager.open_checksum()
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ouverture du checksum: {e}")
    
    def open_converter(self) -> None:
        """Ouvre le convertisseur."""
        try:
            self.tool_manager.open_converter()
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ouverture du convertisseur: {e}")
    
    def on_connection_changed(self, connected: bool) -> None:
        """Gère les changements d'état de connexion."""
        if connected:
            self.connect_button.setText("Déconnecter")
            self.connection_status.setText("Connecté")
            self.port_combo.setEnabled(False)
            self.speed_combo.setEnabled(False)
        else:
            self.connect_button.setText("Connecter")
            self.connection_status.setText("Déconnecté")
            self.port_combo.setEnabled(True)
            self.speed_combo.setEnabled(True)
    
    def on_data_received(self, data: str) -> None:
        """Traite les données reçues."""
        try:
            # Ajouter au buffer
            self._data_buffer.append(data)
            
            # Limiter la taille du buffer
            if len(self._data_buffer) > self.config.max_lines:
                self._data_buffer = self._data_buffer[-self.config.max_lines:]
            
            # Afficher les données
            self.terminal_display_widget.append(data)
            
            # Mettre à jour le compteur
            total_chars = sum(len(line) for line in self._data_buffer)
            self.data_counter.setText(f"{total_chars} octets")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement des données: {e}")
    
    def on_error_occurred(self, error: str) -> None:
        """Gère les erreurs."""
        try:
            self.logger.error(f"Erreur: {error}")
            self.status_bar.showMessage(f"Erreur: {error}", 5000)
            
            # Optionnel: afficher une boîte de dialogue pour les erreurs critiques
            if "critique" in error.lower():
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Erreur Critique", error)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la gestion d'erreur: {e}")
    
    def update_display(self) -> None:
        """Met à jour l'affichage périodiquement."""
        try:
            # Mise à jour des métriques de performance
            if self.memory_optimizer:
                self._performance_metrics['memory_usage'] = self.memory_optimizer.get_memory_usage()
            
            # Mise à jour de l'affichage si nécessaire
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour: {e}")
    
    def optimize_memory(self) -> None:
        """Optimise l'utilisation mémoire."""
        try:
            if self.memory_optimizer:
                self.memory_optimizer.optimize()
                self.logger.debug("Optimisation mémoire effectuée")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'optimisation mémoire: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Retourne les métriques de performance.
        
        Returns:
            Dict[str, Any]: Métriques de performance
        """
        return {
            'is_connected': self._is_connected,
            'buffer_size': len(self._data_buffer),
            'memory_usage': self._performance_metrics.get('memory_usage', 0),
            'refresh_rate': self.config.refresh_rate,
            'max_lines': self.config.max_lines
        }
    
    def closeEvent(self, event) -> None:
        """Gère la fermeture de la fenêtre."""
        try:
            # Sauvegarder la configuration
            if hasattr(self, 'config_manager'):
                self.config_manager.save_config()
            
            # Fermer les connexions
            if self._is_connected:
                self.disconnect_serial()
            
            # Arrêter les timers
            if hasattr(self, 'update_timer'):
                self.update_timer.stop()
            if hasattr(self, 'memory_timer'):
                self.memory_timer.stop()
            
            # Nettoyage mémoire
            if self.memory_optimizer:
                self.memory_optimizer.optimize()
            
            self.logger.info("Fenêtre fermée proprement")
            event.accept()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la fermeture: {e}")
            event.accept()  # Forcer la fermeture même en cas d'erreur


def main() -> None:
    """Fonction principale pour les tests."""
    try:
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        
        # Configuration personnalisée
        config = MainWindowConfig(
            title="CrazyTerm - Test",
            width=1000,
            height=700,
            theme="dark"
        )
        
        # Créer et afficher la fenêtre
        window = MainWindow(config)
        window.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Erreur lors du lancement: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
