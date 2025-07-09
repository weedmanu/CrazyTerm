"""
Outil de conversion de données pour CrazyTerm.
Permet la conversion entre différents formats (texte, hexadécimal, binaire, etc.) avec historique et interface graphique.
"""

from __future__ import annotations
import logging
from typing import Any, Optional, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QHBoxLayout, QMessageBox, QComboBox, QApplication
)

__all__ = ["ToolConverter"]

logger = logging.getLogger("CrazyTerm.ToolConverter")

class ToolConverter(QWidget):
    """
    Convertisseur universel Décimal / Hexadécimal / Binaire / ASCII avec auto-détection.
    """
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialise la fenêtre de conversion de données.
        Args:
            parent (QWidget, optionnel): Widget parent.
        """
        super().__init__(parent)
        self.setWindowTitle("Convertisseur de données")
        self.input_edit = QLineEdit()
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Auto", "Décimal", "Hexadécimal", "Binaire", "ASCII"])
        self.dec_edit = QLineEdit()
        self.hex_edit = QLineEdit()
        self.bin_edit = QLineEdit()
        self.ascii_edit = QLineEdit()
        for edit in (self.dec_edit, self.hex_edit, self.bin_edit, self.ascii_edit):
            edit.setReadOnly(True)
        self.convert_button = QPushButton("Convertir")
        self.copy_button = QPushButton("Copier")
        self.paste_button = QPushButton("Coller")
        self.clear_button = QPushButton("Effacer")
        self.init_ui()
        self.convert_button.clicked.connect(self.convert)
        self.copy_button.clicked.connect(self.copyOutput)
        self.paste_button.clicked.connect(self.pasteInput)
        self.clear_button.clicked.connect(self.clearAll)
        logger.info("ToolConverter initialisé (mode pro, sans historique, conversion manuelle)")

    def init_ui(self) -> None:
        """
        Initialise l'interface utilisateur du convertisseur.
        """
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Entrée :"))
        layout.addWidget(self.input_edit)
        layout.addWidget(QLabel("Format d'entrée :"))
        layout.addWidget(self.format_combo)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.convert_button)
        btn_layout.addWidget(self.copy_button)
        btn_layout.addWidget(self.paste_button)
        btn_layout.addWidget(self.clear_button)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Décimal :"))
        layout.addWidget(self.dec_edit)
        layout.addWidget(QLabel("Hexadécimal :"))
        layout.addWidget(self.hex_edit)
        layout.addWidget(QLabel("Binaire :"))
        layout.addWidget(self.bin_edit)
        layout.addWidget(QLabel("ASCII :"))
        layout.addWidget(self.ascii_edit)
        self.setLayout(layout)

    def clearAll(self) -> None:
        """
        Efface tous les champs de saisie et de sortie.
        """
        self.input_edit.clear()
        self.dec_edit.clear()
        self.hex_edit.clear()
        self.bin_edit.clear()
        self.ascii_edit.clear()

    def copyOutput(self) -> None:
        """
        Copie tous les formats dans le presse-papiers.
        """
        try:
            text = (
                f"Décimal : {self.dec_edit.text()}\n"
                f"Hexadécimal : {self.hex_edit.text()}\n"
                f"Binaire : {self.bin_edit.text()}\n"
                f"ASCII : {self.ascii_edit.text()}"
            )
            clipboard = QApplication.clipboard() if QApplication.instance() else None
            if clipboard is not None and text:
                clipboard.setText(text)
                logger.info("Sorties copiées dans le presse-papiers")
            elif clipboard is None:
                logger.error("Aucune instance QApplication active pour le presse-papiers.")
                QMessageBox.warning(self, "Erreur", "Impossible d'accéder au presse-papiers (QApplication manquant)")
        except Exception as e:
            logger.error(f"Erreur lors de la copie de la sortie : {e}")
            QMessageBox.warning(self, "Erreur", f"Impossible de copier la sortie : {e}")

    def pasteInput(self) -> None:
        """
        Colle le texte du presse-papiers dans la zone d'entrée.
        """
        try:
            self.input_edit.paste()
            logger.info("Entrée collée depuis le presse-papiers")
        except Exception as e:
            logger.error(f"Erreur lors du collage de l'entrée : {e}")
            QMessageBox.warning(self, "Erreur", f"Impossible de coller l'entrée : {e}")

    def convert(self) -> None:
        """
        Effectue la conversion des données saisies et affiche le résultat.
        """
        value = self.input_edit.text().strip()
        fmt = self.format_combo.currentText()
        dec_val = None
        hex_val = ''
        bin_val = ''
        ascii_val = ''
        # Nettoyage des sorties
        self.dec_edit.clear()
        self.hex_edit.clear()
        self.bin_edit.clear()
        self.ascii_edit.clear()
        if not value:
            return
        try:
            if fmt == "Auto":
                # Auto-détection robuste
                if value.isdigit():
                    dec_val = int(value)
                elif value.lower().startswith('0x'):
                    dec_val = int(value, 16)
                elif all(c in '01' for c in value if c not in ' '):
                    dec_val = int(value.replace(' ', ''), 2)
                elif all(32 <= ord(c) <= 126 for c in value):
                    ascii_val = value
                    dec_val = None
                else:
                    raise ValueError("Format non reconnu ou ambigu")
            elif fmt == "Décimal":
                dec_val = int(value)
            elif fmt == "Hexadécimal":
                v = value.lower().replace('0x', '').replace(' ', '')
                dec_val = int(v, 16)
            elif fmt == "Binaire":
                v = value.replace(' ', '')
                dec_val = int(v, 2)
            elif fmt == "ASCII":
                ascii_val = value
                dec_val = None
            # Conversion
            if dec_val is not None:
                if dec_val < 0 or dec_val > 2**64-1:
                    raise ValueError("Valeur hors plage (0 à 2^64-1)")
                hex_val = hex(dec_val)[2:].upper()
                bin_val = bin(dec_val)[2:]
                try:
                    ascii_val = dec_val.to_bytes((dec_val.bit_length() + 7) // 8 or 1, 'big').decode('utf-8', errors='replace')
                except Exception:
                    ascii_val = ''
            if ascii_val and dec_val is None:
                try:
                    dec_val = int.from_bytes(ascii_val.encode('utf-8'), 'big')
                    hex_val = hex(dec_val)[2:].upper()
                    bin_val = bin(dec_val)[2:]
                except Exception:
                    pass
            self.dec_edit.setText(str(dec_val) if dec_val is not None else "")
            self.hex_edit.setText(hex_val)
            self.bin_edit.setText(bin_val)
            self.ascii_edit.setText(ascii_val)
            logger.info(f"Conversion effectuée : {value} -> dec:{dec_val} hex:{hex_val} bin:{bin_val} ascii:{ascii_val}")
        except Exception as e:
            logger.error(f"Erreur lors de la conversion : {e}")
            QMessageBox.warning(self, "Erreur de conversion", f"Entrée invalide ou hors plage : {e}")

    def show(self) -> None:
        """Affiche la fenêtre du convertisseur de données."""
        super().show()
        self.raise_()
        self.activateWindow()