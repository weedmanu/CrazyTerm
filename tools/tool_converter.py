"""
Outil de conversion de données pour CrazyTerm.
Permet la conversion entre différents formats (texte, hexadécimal, binaire, etc.) avec historique et interface graphique.
"""

from __future__ import annotations
import logging
from typing import Any, Optional, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel,
    QHBoxLayout, QListWidget, QMessageBox
)

__all__ = ["DataConverter"]

logger = logging.getLogger("CrazyTerm.ToolConverter")

class DataConverter(QWidget):
    """
    Fenêtre d'outil de conversion de données (texte, hex, binaire, etc.) avec historique.
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
        self.output_edit = QTextEdit()
        self.convert_button = QPushButton("Convertir")
        self.history_list = QListWidget()
        self.copy_button = QPushButton("Copier")
        self.paste_button = QPushButton("Coller")
        self.clear_button = QPushButton("Effacer")
        self.init_ui()
        self.history: List[str] = []
        self.convert_button.clicked.connect(self.convert)
        self.copy_button.clicked.connect(self.copyOutput)
        self.paste_button.clicked.connect(self.pasteInput)
        self.clear_button.clicked.connect(self.clearHistory)
        self.history_list.itemDoubleClicked.connect(self.useHistoryItem)
        self.input_edit.textChanged.connect(self.autoConvert)
        logger.info("DataConverter initialisé")

    def init_ui(self) -> None:
        """
        Initialise l'interface utilisateur du convertisseur.
        """
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Entrée :"))
        layout.addWidget(self.input_edit)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.convert_button)
        btn_layout.addWidget(self.copy_button)
        btn_layout.addWidget(self.paste_button)
        btn_layout.addWidget(self.clear_button)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Sortie :"))
        layout.addWidget(self.output_edit)
        layout.addWidget(QLabel("Historique :"))
        layout.addWidget(self.history_list)
        self.setLayout(layout)

    def updateInputPlaceholder(self) -> None:
        """
        Met à jour le placeholder de la zone d'entrée selon le mode de conversion.
        """
        self.input_edit.setPlaceholderText("Entrez les données à convertir...")

    def addToHistory(self, value: str) -> None:
        """
        Ajoute une valeur à l'historique et à la liste graphique.
        Args:
            value (str): Valeur à ajouter à l'historique.
        """
        try:
            if value and value not in self.history:
                self.history.append(value)
                self.history_list.addItem(value)
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout à l'historique : {e}")
            raise

    def useHistoryItem(self, item: Any) -> None:
        """
        Utilise un élément de l'historique (double-clic).
        Args:
            item (QListWidgetItem): Élément sélectionné.
        """
        if hasattr(item, 'text'):
            self.input_edit.setText(item.text())
        else:
            logger.warning("L'élément d'historique ne possède pas de méthode text().")

    def copyOutput(self) -> None:
        """
        Copie le texte de sortie dans le presse-papiers.
        """
        try:
            text = self.output_edit.toPlainText()
            if text:
                self.output_edit.selectAll()
                self.output_edit.copy()
                logger.info("Sortie copiée dans le presse-papiers")
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
        try:
            value = self.input_edit.text()
            if not value:
                self.output_edit.setPlainText("")
                return
            # Conversion simple : texte <-> hex (exemple)
            if all(c in '0123456789abcdefABCDEF ' for c in value.replace(' ', '')):
                # Hex -> texte
                try:
                    bytes_data = bytes.fromhex(value)
                    result = bytes_data.decode('utf-8', errors='replace')
                except Exception as e:
                    result = f"Erreur de décodage hex : {e}"
            else:
                # Texte -> hex
                try:
                    result = value.encode('utf-8').hex(' ')
                except Exception as e:
                    result = f"Erreur d'encodage texte : {e}"
            self.output_edit.setPlainText(result)
            self.addToHistory(value)
            logger.info(f"Conversion effectuée : {value} -> {result}")
        except Exception as e:
            logger.error(f"Erreur lors de la conversion : {e}")
            self.output_edit.setPlainText(f"Erreur : {e}")

    def autoConvert(self) -> None:
        """
        Conversion automatique à chaque modification de l'entrée.
        """
        self.convert()

    def clearHistory(self) -> None:
        """
        Efface l'historique des conversions.
        """
        try:
            self.history.clear()
            self.history_list.clear()
            logger.info("Historique effacé")
        except Exception as e:
            logger.error(f"Erreur lors de l'effacement de l'historique : {e}")
            raise