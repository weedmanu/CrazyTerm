
"""
Outils de conversion pour CrazyTerm.
Contient des fonctions utilitaires pour la conversion de formats et de données.
"""

from __future__ import annotations

import logging
from typing import Optional
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QGroupBox)

logger = logging.getLogger("CrazySerialTerm.ToolConverter")

class DataConverter(QDialog):
    """Convertisseur de données ASCII/HEX avec interface graphique."""
    def __init__(self, parent: Optional[QDialog] = None) -> None:
        """Initialise la fenêtre de conversion."""
        super().__init__(parent)
        self.setWindowTitle("Convertisseur de Données (ASCII/HEX)")
        self.resize(400, 200)

        layout: QVBoxLayout = QVBoxLayout(self)

        # Zone d'entrée
        inputGroup: QGroupBox = QGroupBox("Données d'entrée")
        inputLayout: QVBoxLayout = QVBoxLayout()
        self.inputText: QTextEdit = QTextEdit()
        self.inputText.setPlaceholderText("Entrez les données à convertir...")
        inputLayout.addWidget(self.inputText)
        inputGroup.setLayout(inputLayout)
        layout.addWidget(inputGroup)

        # Zone de sortie
        outputGroup: QGroupBox = QGroupBox("Données converties")
        outputLayout: QVBoxLayout = QVBoxLayout()
        self.outputText: QTextEdit = QTextEdit()
        self.outputText.setReadOnly(True)
        outputLayout.addWidget(self.outputText)
        outputGroup.setLayout(outputLayout)
        layout.addWidget(outputGroup)

        # Boutons
        buttonLayout: QHBoxLayout = QHBoxLayout()
        self.toHexBtn: QPushButton = QPushButton("Convertir en HEX")
        self.toHexBtn.clicked.connect(self.convertToHex)
        buttonLayout.addWidget(self.toHexBtn)

        self.toAsciiBtn: QPushButton = QPushButton("Convertir en ASCII")
        self.toAsciiBtn.clicked.connect(self.convertToAscii)
        buttonLayout.addWidget(self.toAsciiBtn)

        closeBtn: QPushButton = QPushButton("Fermer")
        closeBtn.clicked.connect(self.accept)
        buttonLayout.addWidget(closeBtn)

        layout.addLayout(buttonLayout)

    def convertToHex(self) -> None:
        """Convertit le texte ASCII en HEX et affiche le résultat."""
        try:
            text: str = self.inputText.toPlainText()
            if not text:
                self.outputText.setText("Aucune donnée à convertir")
                return
            self.outputText.setText(' '.join(f'{ord(c):02X}' for c in text))
            logger.info("Conversion ASCII -> HEX réussie.")
        except Exception as e:
            self.outputText.setText(f"Erreur lors de la conversion: {str(e)}")
            logger.error(f"Erreur conversion ASCII->HEX: {e}")
            
    def convertToAscii(self) -> None:
        """Convertit le texte HEX en ASCII et affiche le résultat."""
        try:
            text: str = self.inputText.toPlainText().replace(' ', '').replace('\n', '').replace('\t', '')
            if not text:
                self.outputText.setText("Aucune donnée à convertir")
                return
            if len(text) % 2 != 0:
                self.outputText.setText("Erreur : nombre impair de caractères HEX")
                return
            self.outputText.setText(bytes.fromhex(text).decode('utf-8', errors='replace'))
            logger.info("Conversion HEX -> ASCII réussie.")
        except ValueError:
            self.outputText.setText("Erreur : données HEX invalides")
            logger.error("Erreur : données HEX invalides")
        except Exception as e:
            self.outputText.setText(f"Erreur lors de la conversion: {str(e)}")
            logger.error(f"Erreur conversion HEX->ASCII: {e}")

    def convert(self) -> None:
        """Convertit les données ASCII/HEX selon le mode sélectionné."""
        try:
            pass  # Logique de conversion à compléter si besoin
        except Exception as e:
            logger.error(f"Erreur lors de la conversion: {e}")
            raise

__all__ = []