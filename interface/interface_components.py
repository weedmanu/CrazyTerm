#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module : interface_components.py

Outil interne CrazyTerm : Panneaux d’interface utilisateur (non natif, chargé dynamiquement)

Rôle :
    Définit les panneaux graphiques principaux de l’interface série de CrazyTerm (personnalisation, connexion, envoi, paramètres avancés).
    Fournit les classes CustomizationPanel, ConnectionPanel, InputPanel, AdvancedSettingsPanel, avec signaux Qt et gestion centralisée de l’UI.

Fonctionnalités principales :
    - Panneaux PyQt5 pour la personnalisation (thème, police, couleurs)
    - Gestion de la connexion série (ports, vitesse, actions)
    - Saisie et envoi de commandes série
    - Paramètres avancés (envoi, affichage, série, log)
    - Signaux Qt pour l’intégration avec la fenêtre principale
    - Méthodes documentées et typées, robustesse et modularité

Dépendances :
    - PyQt5 (QtWidgets, QtCore, QtGui)
    - typing
    - logging
    - (optionnel) serial.tools.list_ports, glob, json, os

Utilisation :
    Ce module est importé par la fenêtre principale et les gestionnaires d’UI pour construire dynamiquement l’interface série et ses outils.
    Chaque panneau peut être instancié et intégré dans un layout PyQt5.

Auteur :
    Projet CrazyTerm (2025) Manu
"""

from __future__ import annotations

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, 
                            QLabel, QComboBox, QPushButton, QCheckBox, QLineEdit, QSpinBox,
                            QColorDialog, QFontDialog, QFileDialog)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont, QColor
from typing import List, Dict, Optional, Union
import logging

logger = logging.getLogger("CrazySerialTerm")

__all__ = []  # À compléter avec les classes/fonctions exportées si besoin

class CustomizationPanel(QWidget):
    """
    Panneau de personnalisation des thèmes et couleurs.
    Permet de choisir le thème, la police et les couleurs du terminal.
    Signaux :
        theme_changed (str)
        font_changed (QFont)
        colors_changed (dict)
    """
    
    # Signaux pour notifier les changements
    theme_changed = pyqtSignal(str)
    font_changed = pyqtSignal(QFont)
    colors_changed = pyqtSignal(dict)
    
    def __init__(self) -> None:
        """
        Initialise le panneau de personnalisation.
        """
        super().__init__()
        self.text_color: QColor = QColor(255, 255, 255)  # Blanc par défaut
        self.bg_color: QColor = QColor(42, 42, 42)  # Gris foncé par défaut
        self.received_color: QColor = QColor(0, 150, 255)  # Bleu par défaut
        self.sent_color: QColor = QColor(0, 255, 0)  # Vert par défaut
        self.send_widgets: List[QWidget] = []
        self.display_widgets: List[QWidget] = []
        self.serial_widgets: List[QWidget] = []
        self.setupUI()
        self.connectSignals()
    
    def setupUI(self) -> None:
        """
        Initialise l'UI du panneau de personnalisation.
        """
        try:
            layout = QVBoxLayout()
            
            # Groupe des thèmes
            theme_group = QGroupBox("Thèmes")
            theme_layout = QVBoxLayout()
            
            theme_select_layout = QHBoxLayout()
            theme_select_layout.addWidget(QLabel("Thème :"))
            self.theme_combo = QComboBox()
            self.theme_combo.addItems(['clair', 'sombre', 'hacker'])
            self.theme_combo.setCurrentText('sombre')
            theme_select_layout.addWidget(self.theme_combo)
            theme_layout.addLayout(theme_select_layout)
            
            theme_group.setLayout(theme_layout)
            layout.addWidget(theme_group)
            
            # Groupe de la police
            font_group = QGroupBox("Police du terminal")
            font_layout = QVBoxLayout()
            
            font_select_layout = QHBoxLayout()
            font_select_layout.addWidget(QLabel("Police :"))
            self.font_combo = QComboBox()
            self.font_combo.addItems(['Consolas', 'Courier New', 'Lucida Console', 'Monospace', 'Arial'])
            self.font_combo.setCurrentText('Consolas')
            font_select_layout.addWidget(self.font_combo)
            font_layout.addLayout(font_select_layout)
            
            size_layout = QHBoxLayout()
            size_layout.addWidget(QLabel("Taille :"))
            self.font_size = QSpinBox()
            self.font_size.setRange(8, 24)
            self.font_size.setValue(12)
            size_layout.addWidget(self.font_size)
            size_layout.addStretch()
            
            self.font_button = QPushButton("Choisir la police...")
            size_layout.addWidget(self.font_button)
            font_layout.addLayout(size_layout)
            
            font_group.setLayout(font_layout)
            layout.addWidget(font_group)
            
            # Groupe des couleurs personnalisées
            color_group = QGroupBox("Couleurs du terminal")
            color_layout = QGridLayout()
            
            # Couleur du texte
            color_layout.addWidget(QLabel("Texte :"), 0, 0)
            self.text_color_btn = QPushButton()
            self.text_color_btn.setFixedSize(50, 30)
            self.text_color = QColor(255, 255, 255)  # Blanc par défaut
            self.text_color_btn.setStyleSheet(f"background-color: {self.text_color.name()}")
            color_layout.addWidget(self.text_color_btn, 0, 1)
            
            # Couleur du fond
            color_layout.addWidget(QLabel("Fond :"), 0, 2)
            self.bg_color_btn = QPushButton()
            self.bg_color_btn.setFixedSize(50, 30)
            self.bg_color = QColor(42, 42, 42)  # Gris foncé par défaut
            self.bg_color_btn.setStyleSheet(f"background-color: {self.bg_color.name()}")
            color_layout.addWidget(self.bg_color_btn, 0, 3)
            
            # Couleur des données reçues
            color_layout.addWidget(QLabel("Données reçues :"), 1, 0)
            self.received_color_btn = QPushButton()
            self.received_color_btn.setFixedSize(50, 30)
            self.received_color = QColor(0, 150, 255)  # Bleu par défaut
            self.received_color_btn.setStyleSheet(f"background-color: {self.received_color.name()}")
            color_layout.addWidget(self.received_color_btn, 1, 1)
            
            # Couleur des données envoyées
            color_layout.addWidget(QLabel("Données envoyées :"), 1, 2)
            self.sent_color_btn = QPushButton()
            self.sent_color_btn.setFixedSize(50, 30)
            self.sent_color = QColor(0, 255, 0)  # Vert par défaut
            self.sent_color_btn.setStyleSheet(f"background-color: {self.sent_color.name()}")
            color_layout.addWidget(self.sent_color_btn, 1, 3)
            
            color_group.setLayout(color_layout)
            layout.addWidget(color_group)
            
            # Boutons d'action
            btn_layout = QHBoxLayout()
            self.apply_btn = QPushButton("Appliquer")
            self.apply_btn.setMinimumWidth(100)
            btn_layout.addWidget(self.apply_btn)
            
            self.reset_btn = QPushButton("Réinitialiser")
            self.reset_btn.setMinimumWidth(100)
            btn_layout.addWidget(self.reset_btn)
            
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            layout.addStretch()
            
            self.setLayout(layout)
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de l'UI: {e}")
            raise
    
    def connectSignals(self) -> None:
        """
        Connecte les signaux des widgets du panneau de personnalisation.
        """
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        self.font_combo.currentTextChanged.connect(self.on_font_changed)
        self.font_size.valueChanged.connect(self.on_font_changed)
        self.font_button.clicked.connect(self.choose_font)
        
        # Boutons de couleur
        self.text_color_btn.clicked.connect(lambda: self.choose_color('text'))
        self.bg_color_btn.clicked.connect(lambda: self.choose_color('bg'))
        self.received_color_btn.clicked.connect(lambda: self.choose_color('received'))
        self.sent_color_btn.clicked.connect(lambda: self.choose_color('sent'))
        
        # Boutons d'action
        self.apply_btn.clicked.connect(self.apply_settings)
        self.reset_btn.clicked.connect(self.reset_settings)
    
    def on_theme_changed(self) -> None:
        """
        Appelé quand le thème change. Émet le signal theme_changed.
        """
        theme = self.theme_combo.currentText()
        self.theme_changed.emit(theme)
    
    def on_font_changed(self) -> None:
        """
        Appelé quand la police change. Émet le signal font_changed.
        """
        font_name = self.font_combo.currentText()
        font_size = self.font_size.value()
        font = QFont(font_name, font_size)
        self.font_changed.emit(font)
    
    def choose_font(self) -> None:
        """
        Ouvre le dialogue de sélection de police et applique la police choisie.
        """
        try:
            current_font = QFont(self.font_combo.currentText(), self.font_size.value())
            font, ok = QFontDialog.getFont(current_font, self)
            if ok:
                self.font_combo.setCurrentText(font.family())
                self.font_size.setValue(font.pointSize())
                self.font_changed.emit(font)
        except Exception as e:
            logger.error(f"Erreur lors du choix de la police : {e}")

    def choose_color(self, color_type: str) -> None:
        """
        Ouvre le dialogue de sélection de couleur et applique la couleur choisie.
        Args:
            color_type (str): Type de couleur à modifier ('text', 'bg', 'received', 'sent').
        """
        try:
            current_color: Optional[QColor] = None
            if color_type == 'text':
                current_color = self.text_color
            elif color_type == 'bg':
                current_color = self.bg_color
            elif color_type == 'received':
                current_color = self.received_color
            elif color_type == 'sent':
                current_color = self.sent_color
            color: QColor = QColorDialog.getColor(current_color, self)
            if color.isValid():
                if color_type == 'text':
                    self.text_color = color
                    self.text_color_btn.setStyleSheet(f"background-color: {color.name()}")
                elif color_type == 'bg':
                    self.bg_color = color
                    self.bg_color_btn.setStyleSheet(f"background-color: {color.name()}")
                elif color_type == 'received':
                    self.received_color = color
                    self.received_color_btn.setStyleSheet(f"background-color: {color.name()}")
                elif color_type == 'sent':
                    self.sent_color = color
                    self.sent_color_btn.setStyleSheet(f"background-color: {color.name()}")
                self.emit_colors_changed()
        except Exception as e:
            logger.error(f"Erreur lors du choix de la couleur : {e}")

    def emit_colors_changed(self) -> None:
        """
        Émet le signal colors_changed avec les couleurs actuelles.
        """
        colors = {
            'text': self.text_color,
            'background': self.bg_color,
            'received': self.received_color,
            'sent': self.sent_color
        }
        self.colors_changed.emit(colors)
    
    def apply_settings(self) -> None:
        """
        Applique tous les paramètres de personnalisation et émet les signaux associés.
        """
        self.on_theme_changed()
        self.on_font_changed()
        self.emit_colors_changed()
        logger.info("Paramètres de personnalisation appliqués")
    
    def reset_settings(self) -> None:
        """
        Remet les paramètres de personnalisation par défaut et met à jour l'UI.
        """
        self.theme_combo.setCurrentText('sombre')
        self.font_combo.setCurrentText('Consolas')
        self.font_size.setValue(12)
        
        # Couleurs par défaut
        self.text_color = QColor(255, 255, 255)
        self.bg_color = QColor(42, 42, 42)
        self.received_color = QColor(0, 150, 255)
        self.sent_color = QColor(0, 255, 0)
        
        # Mettre à jour l'affichage des boutons
        self.text_color_btn.setStyleSheet(f"background-color: {self.text_color.name()}")
        self.bg_color_btn.setStyleSheet(f"background-color: {self.bg_color.name()}")
        self.received_color_btn.setStyleSheet(f"background-color: {self.received_color.name()}")
        self.sent_color_btn.setStyleSheet(f"background-color: {self.sent_color.name()}")
        
        self.apply_settings()
        logger.info("Paramètres de personnalisation remis par défaut")

class ConnectionPanel(QGroupBox):
    """
    Panneau de configuration de connexion série classique.
    Permet de sélectionner le port, la vitesse et de gérer la connexion.
    Signaux :
        connect_requested
        disconnect_requested
        refresh_requested
        clear_requested
    """
    
    connect_requested = pyqtSignal()
    disconnect_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    
    def __init__(self) -> None:
        """
        Initialise le panneau de connexion série.
        """
        super().__init__("Paramètres de connexion")
        self.setupUI()
        self.connectSignals()
    
    def setupUI(self) -> None:
        """
        Initialise l'UI du panneau de connexion.
        """
        layout = QHBoxLayout()
        
        # Port série
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel('Port:'))
        self.port_select = QComboBox()
        self.port_select.setMinimumWidth(100)
        port_layout.addWidget(self.port_select)
        layout.addLayout(port_layout)
        
        # Bouton de rafraîchissement
        self.refresh_btn = QPushButton('Rafraîchir')
        self.refresh_btn.setMinimumWidth(80)
        layout.addWidget(self.refresh_btn)
        
        # Vitesse
        baud_layout = QHBoxLayout()
        baud_layout.addWidget(QLabel('Vitesse:'))
        self.baud_select = QComboBox()
        self.baud_select.addItems(['9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600'])
        self.baud_select.setCurrentText('115200')
        self.baud_select.setMinimumWidth(80)
        baud_layout.addWidget(self.baud_select)
        layout.addLayout(baud_layout)
        
        # Bouton de connexion
        self.connect_btn = QPushButton('Connecter')
        self.connect_btn.setMinimumWidth(100)
        layout.addWidget(self.connect_btn)
        
        # Bouton pour effacer
        self.clear_btn = QPushButton('Effacer')
        self.clear_btn.setMinimumWidth(80)
        layout.addWidget(self.clear_btn)
        
        self.setLayout(layout)
    
    def connectSignals(self) -> None:
        """
        Connecte les signaux des widgets du panneau de connexion.
        """
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        self.clear_btn.clicked.connect(self.clear_requested.emit)
    
    def on_connect_clicked(self) -> None:
        """
        Gère le clic sur le bouton de connexion/déconnexion.
        """
        if self.connect_btn.text() == 'Connecter':
            self.connect_requested.emit()
        else:
            self.disconnect_requested.emit()
    
    def set_connected(self, connected: bool) -> None:
        """
        Met à jour l'état de connexion dans l'interface.
        Args:
            connected (bool): True si connecté, False sinon.
        """
        if connected:
            self.connect_btn.setText('Déconnecter')
        else:
            self.connect_btn.setText('Connecter')
    
    def update_ports(self, ports: List[str]) -> None:
        """
        Met à jour la liste des ports disponibles.
        Args:
            ports (List[str]): Liste des ports série détectés.
        """
        current_port = self.port_select.currentText()
        self.port_select.clear()
        if ports:
            self.port_select.addItems(ports)
            if current_port in ports:
                self.port_select.setCurrentText(current_port)
    
    def get_connection_params(self) -> Dict[str, Union[str, int]]:
        """
        Retourne les paramètres de connexion sélectionnés.
        Returns:
            Dict[str, Union[str, int]]: Dictionnaire avec 'port' et 'baudrate'.
        """
        return {
            'port': self.port_select.currentText(),
            'baudrate': int(self.baud_select.currentText())
        }
    
    def refresh_ports(self) -> None:
        """
        Rafraîchit la liste des ports série disponibles (cross-platform, robuste et performant).
        """
        try:
            import sys
            if sys.platform.startswith('win'):
                import serial.tools.list_ports
                ports = [port.device for port in serial.tools.list_ports.comports()]
            elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                import glob
                ports = glob.glob('/dev/tty[A-Za-z]*')
            elif sys.platform.startswith('darwin'):
                import glob
                ports = glob.glob('/dev/tty.*')
            else:
                ports = []
            self.update_ports(ports)
            logger.info(f"Ports série détectés : {ports}")
        except Exception as e:
            logger.error(f"Erreur lors du scan des ports série : {e}")
            self.update_ports([])

class InputPanel(QGroupBox):
    """
    Panneau d'envoi de données.
    Permet de saisir et d'envoyer des commandes sur le port série.
    Signal :
        send_requested (str)
    """
    
    send_requested = pyqtSignal(str)
    
    def __init__(self) -> None:
        """
        Initialise le panneau d'envoi de données.
        """
        super().__init__("Envoi de données")
        self.setupUI()
        self.connectSignals()
    
    def setupUI(self) -> None:
        """
        Initialise l'UI du panneau d'envoi de données.
        """
        layout = QVBoxLayout()
        
        # Zone de saisie et bouton
        send_layout = QHBoxLayout()
        send_layout.addWidget(QLabel("Commande :"))
        self.input_field = QLineEdit()
        send_layout.addWidget(self.input_field, 4)
        
        self.send_btn = QPushButton('Envoyer')
        self.send_btn.setMinimumWidth(80)
        send_layout.addWidget(self.send_btn)
        
        layout.addLayout(send_layout)
        self.setLayout(layout)
    
    def connectSignals(self) -> None:
        """
        Connecte les signaux des widgets du panneau d'envoi.
        """
        self.send_btn.clicked.connect(self.on_send_clicked)
        self.input_field.returnPressed.connect(self.on_send_clicked)
    
    def on_send_clicked(self) -> None:
        """
        Gère le clic sur le bouton d'envoi ou la touche Entrée.
        """
        try:
            text = self.input_field.text()
            if text:
                self.send_requested.emit(text)
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la commande : {e}")
    
    def clear_input(self) -> None:
        """
        Efface le champ d'entrée.
        """
        self.input_field.clear()
    
    def set_text(self, text: str) -> None:
        """
        Définit le texte dans le champ d'entrée.
        Args:
            text (str): Texte à afficher dans le champ d'entrée.
        """
        self.input_field.setText(text)
    
    def get_text(self) -> str:
        """
        Retourne le texte du champ d'entrée.
        Returns:
            str: Texte courant du champ d'entrée.
        """
        return self.input_field.text()

class AdvancedSettingsPanel(QWidget):
    """
    Panneau des paramètres avancés pour la communication série.
    Permet de configurer les options d'envoi, d'affichage et série avancées.
    Signaux :
        settings_changed
        send_settings_changed (dict)
        display_settings_changed (dict)
        serial_settings_changed (dict)
    """
    
    # Signaux pour notifier les changements
    settings_changed = pyqtSignal()
    send_settings_changed = pyqtSignal(dict)
    display_settings_changed = pyqtSignal(dict)
    serial_settings_changed = pyqtSignal(dict)
    
    def __init__(self) -> None:
        """
        Initialise le panneau des paramètres avancés.
        """
        super().__init__()
        self.setupUI()
        self.connectSignals()
        self.init_group_states()
    
    def init_group_states(self) -> None:
        """
        Initialise l'état des groupes selon leur état coché/décoché.
        """
        self.on_send_group_toggled(self.send_group.isChecked())
        self.on_display_group_toggled(self.display_group.isChecked())
        self.on_serial_group_toggled(self.serial_group.isChecked())
    
    def setupUI(self) -> None:
        """
        Initialise l'UI du panneau des paramètres avancés.
        """
        layout = QVBoxLayout()
        
        # Groupe pour les options d'envoi
        self.send_group = QGroupBox("Options d'envoi")
        self.send_group.setCheckable(True)
        self.send_group.setChecked(True)  # Coché par défaut
        send_layout = QGridLayout()
        
        # Fin de ligne
        self.eol_label = QLabel('Fin de ligne :')
        send_layout.addWidget(self.eol_label, 0, 2)
        self.eol_select = QComboBox()
        self.eol_select.addItems(['Aucun', 'NL', 'CR', 'NL+CR'])
        self.eol_select.setCurrentText('NL+CR')  # NL+CR par défaut
        send_layout.addWidget(self.eol_select, 0, 3)
        
        # Répétition
        self.repeat_check = QCheckBox('Répéter')
        send_layout.addWidget(self.repeat_check, 1, 0)
        
        # Intervalle
        self.interval_label = QLabel('Intervalle (ms) :')
        send_layout.addWidget(self.interval_label, 1, 2)
        self.repeat_interval = QLineEdit('1000')
        self.repeat_interval.setFixedWidth(60)
        send_layout.addWidget(self.repeat_interval, 1, 3)
        
        # Options d'envoi sur une seule ligne
        send_layout = QGridLayout()
        send_layout.addWidget(self.eol_label, 0, 0)
        send_layout.addWidget(self.eol_select, 0, 1)
        send_layout.addWidget(self.repeat_check, 0, 2)
        send_layout.addWidget(self.interval_label, 0, 3)
        send_layout.addWidget(self.repeat_interval, 0, 4)
        
        self.send_group.setLayout(send_layout)
        
        # Stocker les widgets du groupe d'envoi pour la gestion de visibilité
        self.send_widgets = [
            self.eol_label, self.eol_select,
            self.repeat_check,
            self.interval_label, self.repeat_interval
        ]
        
        # Masquer le contenu initialement (groupe décoché par défaut)
        self.send_group.setFlat(False)
        layout.addWidget(self.send_group)
        
        # Groupe pour les options d'affichage
        self.display_group = QGroupBox("Options d'affichage")
        self.display_group.setCheckable(True)
        self.display_group.setChecked(False)  # Décoché par défaut
        display_layout = QGridLayout()
        
        # Format d'affichage
        self.display_format_label = QLabel('Format d\'affichage:')
        display_layout.addWidget(self.display_format_label, 0, 0)
        self.display_format = QComboBox()
        self.display_format.addItems(['ASCII', 'HEX', 'Les deux'])
        display_layout.addWidget(self.display_format, 0, 1)
        
        # Options d'affichage
        self.auto_scroll_check = QCheckBox('Défilement automatique')
        self.auto_scroll_check.setChecked(True)
        display_layout.addWidget(self.auto_scroll_check, 1, 0, 1, 2)
        
        self.timestamp_check = QCheckBox('Afficher timestamps')
        display_layout.addWidget(self.timestamp_check, 2, 0, 1, 2)
        
        self.display_group.setLayout(display_layout)
        
        # Stocker les widgets du groupe d'affichage
        self.display_widgets = [
            self.display_format_label, self.display_format,
            self.auto_scroll_check, self.timestamp_check
        ]
        
        layout.addWidget(self.display_group)
        
        # Groupe pour les paramètres de connexion avancés
        self.serial_group = QGroupBox("Paramètres de connexion avancés")
        self.serial_group.setCheckable(True)
        self.serial_group.setChecked(False)  # Décoché par défaut
        serial_layout = QGridLayout()
        
        # Paramètres série
        self.data_label = QLabel('Bits de données:')
        serial_layout.addWidget(self.data_label, 0, 0)
        self.data_select = QComboBox()
        self.data_select.addItems(['5', '6', '7', '8'])
        self.data_select.setCurrentText('8')
        serial_layout.addWidget(self.data_select, 0, 1)
        
        self.parity_label = QLabel('Parité:')
        serial_layout.addWidget(self.parity_label, 0, 2)
        self.parity_select = QComboBox()
        self.parity_select.addItems(['Aucune', 'Paire', 'Impaire'])
        serial_layout.addWidget(self.parity_select, 0, 3)
        
        self.stop_label = QLabel('Bits de stop:')
        serial_layout.addWidget(self.stop_label, 1, 0)
        self.stop_select = QComboBox()
        self.stop_select.addItems(['1', '1.5', '2'])
        serial_layout.addWidget(self.stop_select, 1, 1)
        
        self.flow_label = QLabel('Contrôle de flux:')
        serial_layout.addWidget(self.flow_label, 1, 2)
        self.flow_select = QComboBox()
        self.flow_select.addItems(['Aucun', 'XON/XOFF', 'RTS/CTS', 'DSR/DTR'])
        serial_layout.addWidget(self.flow_select, 1, 3)
        
        self.serial_group.setLayout(serial_layout)
        
        # Stocker les widgets du groupe série
        self.serial_widgets = [
            self.data_label, self.data_select,
            self.parity_label, self.parity_select,
            self.stop_label, self.stop_select,
            self.flow_label, self.flow_select
        ]
        
        layout.addWidget(self.serial_group)
        
        # Groupe pour l'historique des commandes envoyées
        self.log_group = QGroupBox("Historique des commandes envoyées")
        log_layout = QHBoxLayout()
        self.log_enabled_check = QCheckBox("Activer l'historique dans un fichier log")
        self.log_enabled_check.setChecked(False)
        log_layout.addWidget(self.log_enabled_check)
        self.log_path_edit = QLineEdit('serial_terminal.log')
        self.log_path_edit.setPlaceholderText("Chemin du fichier log")
        log_layout.addWidget(self.log_path_edit)
        self.log_browse_btn = QPushButton("...")
        log_layout.addWidget(self.log_browse_btn)
        self.log_group.setLayout(log_layout)
        layout.addWidget(self.log_group)
        
        # Boutons de sauvegarde/restauration
        btn_layout = QHBoxLayout()
        # self.save_btn = QPushButton("Sauvegarder les paramètres")
        # self.save_btn.setMinimumWidth(150)
        # btn_layout.addWidget(self.save_btn)
        # self.load_btn = QPushButton("Restaurer les paramètres")
        # self.load_btn.setMinimumWidth(150)
        # btn_layout.addWidget(self.load_btn)
        self.reset_btn = QPushButton("Réinitialiser")
        self.reset_btn.setMinimumWidth(100)
        btn_layout.addWidget(self.reset_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def connectSignals(self) -> None:
        """
        Connecte les signaux des widgets du panneau avancé.
        """
        # Signaux des groupes (cocher/décocher)
        self.send_group.toggled.connect(self.on_send_group_toggled)
        self.display_group.toggled.connect(self.on_display_group_toggled)
        self.serial_group.toggled.connect(self.on_serial_group_toggled)
        
        # Signaux des paramètres d'envoi
        self.eol_select.currentTextChanged.connect(self.on_send_settings_changed)
        self.repeat_check.toggled.connect(self.on_send_settings_changed)
        self.repeat_interval.textChanged.connect(self.on_send_settings_changed)
        
        # Signaux des paramètres d'affichage
        self.display_format.currentTextChanged.connect(self.on_display_settings_changed)
        self.auto_scroll_check.toggled.connect(self.on_display_settings_changed)
        self.timestamp_check.toggled.connect(self.on_display_settings_changed)
        
        # Signaux des paramètres série
        self.data_select.currentTextChanged.connect(self.on_serial_settings_changed)
        self.parity_select.currentTextChanged.connect(self.on_serial_settings_changed)
        self.stop_select.currentTextChanged.connect(self.on_serial_settings_changed)
        self.flow_select.currentTextChanged.connect(self.on_serial_settings_changed)
        
        # Signaux des paramètres de log
        self.log_enabled_check.toggled.connect(self.on_log_settings_changed)
        self.log_path_edit.textChanged.connect(self.on_log_settings_changed)
        self.log_browse_btn.clicked.connect(self.browse_log_file)
        
        # Signaux des boutons
        self.reset_btn.clicked.connect(self.reset_settings)
    
    def on_send_group_toggled(self, checked: bool) -> None:
        """
        Appelé quand le groupe d'envoi est coché/décoché.
        Args:
            checked (bool): True si le groupe est coché.
        """
        # Masquer/afficher tous les widgets du groupe
        for widget in self.send_widgets:
            widget.setVisible(checked)
        
        if checked:
            self.on_send_settings_changed()
    
    def on_display_group_toggled(self, checked: bool) -> None:
        """
        Appelé quand le groupe d'affichage est coché/décoché.
        Args:
            checked (bool): True si le groupe est coché.
        """
        # Masquer/afficher tous les widgets du groupe
        for widget in self.display_widgets:
            widget.setVisible(checked)
        
        if checked:
            self.on_display_settings_changed()
    
    def on_serial_group_toggled(self, checked: bool) -> None:
        """
        Appelé quand le groupe série est coché/décoché.
        Args:
            checked (bool): True si le groupe est coché.
        """
        # Masquer/afficher tous les widgets du groupe
        for widget in self.serial_widgets:
            widget.setVisible(checked)
        
        if checked:
            self.on_serial_settings_changed()
    
    def on_send_settings_changed(self) -> None:
        """
        Appelé quand les paramètres d'envoi changent. Émet le signal associé.
        """
        if self.send_group.isChecked():
            settings = self.get_send_settings()
            self.send_settings_changed.emit(settings)
    
    def on_display_settings_changed(self) -> None:
        """
        Appelé quand les paramètres d'affichage changent. Émet le signal associé.
        """
        if self.display_group.isChecked():
            settings = self.get_display_settings()
            self.display_settings_changed.emit(settings)
    
    def on_serial_settings_changed(self) -> None:
        """
        Appelé quand les paramètres série changent. Émet le signal associé.
        """
        if self.serial_group.isChecked():
            settings = self.get_serial_settings()
            self.serial_settings_changed.emit(settings)
    
    def on_log_settings_changed(self) -> None:
        """
        Appelé quand les paramètres de log changent. Émet le signal associé.
        """
        settings = self.get_log_settings()
        self.settings_changed.emit()
        # Optionnel : signal dédié si besoin
    
    def browse_log_file(self) -> None:
        """
        Ouvre un dialogue pour choisir le fichier log.
        """
        path, _ = QFileDialog.getSaveFileName(self, "Choisir le fichier log", self.log_path_edit.text(), "Fichiers log (*.log);;Tous les fichiers (*)")
        if path:
            self.log_path_edit.setText(path)
    
    def get_log_settings(self) -> Dict[str, object]:
        """
        Retourne les paramètres de log.
        Returns:
            Dict[str, object]: Dictionnaire des paramètres de log.
        """
        return {
            'enabled': self.log_enabled_check.isChecked(),
            'path': self.log_path_edit.text()
        }
    
    def save_settings(self) -> None:
        """
        Sauvegarde les paramètres actuels dans le fichier centralisé config/settings.json.
        """
        try:
            import json
            import os
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json')
            config_path = os.path.normpath(config_path)
            settings = {
                'send_group_enabled': self.send_group.isChecked(),
                'display_group_enabled': self.display_group.isChecked(),
                'serial_group_enabled': self.serial_group.isChecked(),
                'send_settings': self.get_send_settings(),
                'display_settings': self.get_display_settings(),
                'serial_settings': self.get_serial_settings(),
                'log_settings': self.get_log_settings(),
            }
            with open(config_path, 'r', encoding='utf-8') as f:
                all_settings = json.load(f)
            all_settings['advanced_settings'] = settings
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(all_settings, f, indent=2)
            logger.info("Paramètres avancés sauvegardés dans config/settings.json")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des paramètres avancés: {e}")

    def load_settings(self) -> None:
        """
        Charge les paramètres avancés depuis le fichier centralisé config/settings.json.
        """
        try:
            import json
            import os
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json')
            config_path = os.path.normpath(config_path)
            with open(config_path, 'r', encoding='utf-8') as f:
                all_settings = json.load(f)
            settings = all_settings.get('advanced_settings', {})
            # Restaurer l'état des groupes
            self.send_group.setChecked(settings.get('send_group_enabled', False))
            self.display_group.setChecked(settings.get('display_group_enabled', False))
            self.serial_group.setChecked(settings.get('serial_group_enabled', False))
            # Restaurer les paramètres d'envoi
            send_settings = settings.get('send_settings', {})
            if 'eol' in send_settings:
                self.eol_select.setCurrentText(send_settings['eol'])
            if 'repeat' in send_settings:
                self.repeat_check.setChecked(send_settings['repeat'])
            if 'interval' in send_settings:
                self.repeat_interval.setText(str(send_settings['interval']))
            
            # Restaurer les paramètres d'affichage
            display_settings = settings.get('display_settings', {})
            if 'format' in display_settings:
                self.display_format.setCurrentText(display_settings['format'])
            if 'auto_scroll' in display_settings:
                self.auto_scroll_check.setChecked(display_settings['auto_scroll'])
            if 'timestamp' in display_settings:
                self.timestamp_check.setChecked(display_settings['timestamp'])
            
            # Restaurer les paramètres série
            serial_settings = settings.get('serial_settings', {})
            if 'bytesize' in serial_settings:
                self.data_select.setCurrentText(str(serial_settings['bytesize']))
            if 'parity' in serial_settings:
                parity_reverse_map = {'N': 'Aucune', 'E': 'Paire', 'O': 'Impaire'}
                self.parity_select.setCurrentText(parity_reverse_map.get(serial_settings['parity'], 'Aucune'))
            if 'stopbits' in serial_settings:
                self.stop_select.setCurrentText(str(serial_settings['stopbits']))
            
            # Restaurer les paramètres de log
            log_settings = settings.get('log_settings', {})
            self.log_enabled_check.setChecked(log_settings.get('enabled', False))
            self.log_path_edit.setText(log_settings.get('path', 'serial_terminal.log'))
            
            logger.info("Paramètres avancés chargés")
        except FileNotFoundError:
            logger.info("Aucun fichier de paramètres trouvé")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des paramètres: {e}")
    
    def reset_settings(self) -> None:
        """
        Remet les paramètres avancés par défaut et met à jour l'UI.
        """
        # Décocher tous les groupes
        self.send_group.setChecked(False)
        self.display_group.setChecked(False)
        self.serial_group.setChecked(False)
        
        # Remettre les valeurs par défaut
        self.eol_select.setCurrentText('NL+CR')
        self.repeat_check.setChecked(False)
        self.repeat_interval.setText('1000')
        self.display_format.setCurrentText('ASCII')
        self.auto_scroll_check.setChecked(True)
        self.timestamp_check.setChecked(False)
        self.data_select.setCurrentText('8')
        self.parity_select.setCurrentText('Aucune')
        self.stop_select.setCurrentText('1')
        self.flow_select.setCurrentText('Aucun')
        self.log_enabled_check.setChecked(False)
        self.log_path_edit.setText('serial_terminal.log')
        
        logger.info("Paramètres remis par défaut")
    
    def get_send_settings(self) -> Dict[str, Union[str, bool]]:
        """
        Retourne les paramètres d'envoi.
        Returns:
            Dict[str, Union[str, bool]]: Dictionnaire des paramètres d'envoi.
        """
        return {
            'format': 'ASCII',  # Toujours ASCII
            'eol': self.eol_select.currentText(),
            'repeat': self.repeat_check.isChecked(),
            'interval': self.repeat_interval.text()
        }
    
    def get_display_settings(self) -> Dict[str, Union[str, bool]]:
        """
        Retourne les paramètres d'affichage.
        Returns:
            Dict[str, Union[str, bool]]: Dictionnaire des paramètres d'affichage.
        """
        return {
            'format': self.display_format.currentText(),
            'auto_scroll': self.auto_scroll_check.isChecked(),
            'timestamp': self.timestamp_check.isChecked()
        }
    
    def get_serial_settings(self) -> Dict[str, Union[int, str, float, bool]]:
        """
        Retourne les paramètres série avancés.
        Returns:
            Dict[str, Union[int, str, float, bool]]: Dictionnaire des paramètres série.
        """
        parity_map = {'Aucune': 'N', 'Paire': 'E', 'Impaire': 'O'}
        stop_bits_map = {'1': 1, '1.5': 1.5, '2': 2}
        flow_control_map = {
            'Aucun': {'xonxoff': False, 'rtscts': False, 'dsrdtr': False},
            'XON/XOFF': {'xonxoff': True, 'rtscts': False, 'dsrdtr': False},
            'RTS/CTS': {'xonxoff': False, 'rtscts': True, 'dsrdtr': False},
            'DSR/DTR': {'xonxoff': False, 'rtscts': False, 'dsrdtr': True}
        }
        return {
            'bytesize': int(self.data_select.currentText()),
            'parity': parity_map[self.parity_select.currentText()],
            'stopbits': stop_bits_map[self.stop_select.currentText()],
            **flow_control_map[self.flow_select.currentText()]
        }
    
    def get_all_settings(self) -> dict:
        """
        Retourne tous les paramètres avancés sous forme de dictionnaire, y compris l'état des groupes et cases à cocher connexes.
        """
        settings = {
            'send_group_enabled': self.send_group.isChecked(),
            'display_group_enabled': self.display_group.isChecked(),
            'serial_group_enabled': self.serial_group.isChecked(),
            'send_settings': self.get_send_settings(),
            'display_settings': self.get_display_settings(),
            'serial_settings': self.get_serial_settings(),
            'log_settings': self.get_log_settings(),
        }
        # Ajout état des cases à cocher du ConnectionPanel si accessible
        if hasattr(self.parent(), 'serial_panel') and self.parent().serial_panel:
            panel = self.parent().serial_panel
            if hasattr(panel, 'port_select'):
                settings['connection_panel_port'] = panel.port_select.currentText()
            if hasattr(panel, 'baud_select'):
                settings['connection_panel_baud'] = panel.baud_select.currentText()
        # Ajout état du InputPanel (rien à sauvegarder sauf si on veut le texte)
        return settings

    def set_all_settings(self, settings: dict) -> None:
        """
        Applique tous les paramètres avancés depuis un dictionnaire, y compris l'état des groupes et cases à cocher connexes.
        """
        # Restaurer l'état des groupes
        self.send_group.setChecked(settings.get('send_group_enabled', False))
        self.display_group.setChecked(settings.get('display_group_enabled', False))
        self.serial_group.setChecked(settings.get('serial_group_enabled', False))
        # Restaurer les paramètres d'envoi
        send_settings = settings.get('send_settings', {})
        if 'eol' in send_settings:
            self.eol_select.setCurrentText(send_settings['eol'])
        if 'repeat' in send_settings:
            self.repeat_check.setChecked(send_settings['repeat'])
        if 'interval' in send_settings:
            self.repeat_interval.setText(str(send_settings['interval']))
        # Restaurer les paramètres d'affichage
        display_settings = settings.get('display_settings', {})
        if 'format' in display_settings:
            self.display_format.setCurrentText(display_settings['format'])
        if 'auto_scroll' in display_settings:
            self.auto_scroll_check.setChecked(display_settings['auto_scroll'])
        if 'timestamp' in display_settings:
            self.timestamp_check.setChecked(display_settings['timestamp'])
        # Restaurer les paramètres série
        serial_settings = settings.get('serial_settings', {})
        if 'bytesize' in serial_settings:
            self.data_select.setCurrentText(str(serial_settings['bytesize']))
        if 'parity' in serial_settings:
            parity_reverse_map = {'N': 'Aucune', 'E': 'Paire', 'O': 'Impaire'}
            self.parity_select.setCurrentText(parity_reverse_map.get(serial_settings['parity'], 'Aucune'))
        if 'stopbits' in serial_settings:
            self.stop_select.setCurrentText(str(serial_settings['stopbits']))
        # Restaurer les paramètres de log
        log_settings = settings.get('log_settings', {})
        self.log_enabled_check.setChecked(log_settings.get('enabled', False))
        self.log_path_edit.setText(log_settings.get('path', 'serial_terminal.log'))
        # Restaurer état du ConnectionPanel si présent
        if 'connection_panel_port' in settings and hasattr(self.parent(), 'serial_panel'):
            panel = self.parent().serial_panel
            if hasattr(panel, 'port_select'):
                idx = panel.port_select.findText(settings['connection_panel_port'])
                if idx >= 0:
                    panel.port_select.setCurrentIndex(idx)
        if 'connection_panel_baud' in settings and hasattr(self.parent(), 'serial_panel'):
            panel = self.parent().serial_panel
            if hasattr(panel, 'baud_select'):
                idx = panel.baud_select.findText(settings['connection_panel_baud'])
                if idx >= 0:
                    panel.baud_select.setCurrentIndex(idx)
