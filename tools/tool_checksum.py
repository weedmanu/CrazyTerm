#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module : tool_checksum.py

Outil externe CrazyTerm : Calcul de checksums (non natif, chargé dynamiquement)

Rôle :
    Fournit une interface graphique pour calculer différents types de checksums (CRC, MD5, SHA, etc.)
    sur des données saisies ou importées dans CrazyTerm.

Fonctionnalités principales :
    - Calcul de checksums standards (CRC8, CRC16, CRC32, MD5, SHA1, SHA256, etc.)
    - Interface utilisateur PyQt5 intuitive
    - Prise en charge de l'encodage hexadécimal, ASCII, binaire
    - Affichage détaillé des résultats et options de copie

Dépendances :
    - PyQt5
    - hashlib
    - binascii

Utilisation :
    Ce module est chargé dynamiquement par le gestionnaire d’outils de CrazyTerm.
    Il permet de vérifier l'intégrité ou l'identité de données transmises.

Auteur :
    Projet CrazyTerm (2025) Manu
"""

from __future__ import annotations

import hashlib
import logging
from typing import Optional, Dict
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QTextEdit, QLineEdit, QPushButton, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt

logger = logging.getLogger("CrazySerialTerm.ToolChecksum")

class ChecksumCalculator(QDialog):
    """
    Calculatrice de checksums et de hash (MD5, SHA, CRC, etc.) pour des données ASCII ou HEX.
    Fournit une interface utilisateur pour saisir des données, choisir le format, et obtenir les résultats.
    """
    def __init__(self, parent: Optional[QDialog] = None) -> None:
        """
        Initialise la fenêtre de calcul de checksums.
        Args:
            parent (Optional[QDialog]): Fenêtre parente éventuelle.
        Returns:
            None
        """
        super().__init__(parent)
        self.setWindowTitle("Calculatrice de Checksums")
        self.resize(500, 300)
        
        layout: QVBoxLayout = QVBoxLayout(self)
        
        # Zone d'entrée
        inputGroup: QGroupBox = QGroupBox("Données d'entrée")
        inputLayout: QVBoxLayout = QVBoxLayout()
        
        formatLayout: QHBoxLayout = QHBoxLayout()
        formatLayout.addWidget(QLabel("Format:"))
        self.formatSelect: QComboBox = QComboBox()
        self.formatSelect.addItems(["ASCII", "HEX"])
        self.formatSelect.currentIndexChanged.connect(self.calculateChecksums)
        formatLayout.addWidget(self.formatSelect)
        inputLayout.addLayout(formatLayout)
        
        self.dataInput: QTextEdit = QTextEdit()
        self.dataInput.setPlaceholderText("Entrez les données à traiter...")
        self.dataInput.textChanged.connect(self.calculateChecksums)
        inputLayout.addWidget(self.dataInput)
        
        inputGroup.setLayout(inputLayout)
        layout.addWidget(inputGroup)
        
        # Zone de résultats
        resultsGroup: QGroupBox = QGroupBox("Résultats")
        resultsLayout: QGridLayout = QGridLayout()
        
        # Définir les types de checksums
        checksums = [
            ("Somme", "Sum"),
            ("XOR", "XOR"),
            ("CRC8", "CRC-8"),
            ("CRC16", "CRC-16"),
            ("CRC32", "CRC-32"),
            ("MD5", "MD5"),
            ("SHA-1", "SHA-1"),
            ("SHA-256", "SHA-256")
        ]
        
        self.results: Dict[str, QLineEdit] = {}
        row: int = 0
        for name, key in checksums:
            resultsLayout.addWidget(QLabel(f"{name}:"), row, 0)
            self.results[key] = QLineEdit()
            self.results[key].setReadOnly(True)
            resultsLayout.addWidget(self.results[key], row, 1)
            row += 1
            
        resultsGroup.setLayout(resultsLayout)
        layout.addWidget(resultsGroup)
        
        # Boutons
        buttonLayout: QHBoxLayout = QHBoxLayout()
        clearBtn: QPushButton = QPushButton("Effacer")
        clearBtn.clicked.connect(self.clearData)
        buttonLayout.addWidget(clearBtn)
        
        closeBtn: QPushButton = QPushButton("Fermer")
        closeBtn.clicked.connect(self.accept)
        buttonLayout.addWidget(closeBtn)
        
        layout.addLayout(buttonLayout)
        
    def calculateChecksums(self) -> None:
        """
        Calcule les checksums et met à jour l'affichage.
        Args:
            None
        Returns:
            None
        Raises:
            Exception: En cas d'erreur de calcul ou de conversion des données.
        """
        try:
            text: str = self.dataInput.toPlainText()
            if not text:
                self.clearResults()
                return
                
            # Convertir les données selon le format
            if self.formatSelect.currentText() == "ASCII":
                data: bytes = text.encode('utf-8')
            else:  # HEX
                hex_text: str = ''.join(c for c in text if c.upper() in '0123456789ABCDEF ')
                hex_text = hex_text.replace(' ', '')
                if len(hex_text) % 2 != 0: 
                    hex_text += '0'
                try: 
                    data = bytes.fromhex(hex_text)
                except ValueError: 
                    self.clearResults()
                    return
            
            # Calculer les checksums
            self.results["Sum"].setText(f"{sum(data) & 0xFF:02X}")
            
            xor_result: int = 0
            for b in data: 
                xor_result ^= b
            self.results["XOR"].setText(f"{xor_result:02X}")
            
            # CRC8
            crc8: int = 0
            for b in data:
                crc8 ^= b
                for _ in range(8): 
                    crc8 = (crc8 << 1) ^ 0x07 if crc8 & 0x80 else crc8 << 1
                crc8 &= 0xFF
            self.results["CRC-8"].setText(f"{crc8:02X}")

            # CRC16
            crc16: int = 0xFFFF
            for b in data:
                crc16 ^= b << 8
                for _ in range(8): 
                    crc16 = (crc16 << 1) ^ 0x1021 if crc16 & 0x8000 else crc16 << 1
                crc16 &= 0xFFFF
            self.results["CRC-16"].setText(f"{crc16:04X}")

            # CRC32
            crc32: int = 0xFFFFFFFF
            for b in data:
                crc32 ^= b
                for _ in range(8): 
                    crc32 = (crc32 >> 1) ^ 0xEDB88320 if crc32 & 1 else crc32 >> 1
            crc32 ^= 0xFFFFFFFF
            self.results["CRC-32"].setText(f"{crc32:08X}")

            # Hash algorithms
            self.results["MD5"].setText(hashlib.md5(data).hexdigest().upper())
            self.results["SHA-1"].setText(hashlib.sha1(data).hexdigest().upper())
            self.results["SHA-256"].setText(hashlib.sha256(data).hexdigest().upper())

            logger.info("Checksums calculés avec succès.")
        except Exception as e:
            logger.error(f"Erreur lors du calcul des checksums: {e}")
            raise

    def clearData(self) -> None:
        """
        Efface la zone de saisie et les résultats.
        Args:
            None
        Returns:
            None
        """
        self.dataInput.clear()
        self.clearResults()
        logger.debug("Données effacées.")

    def clearResults(self) -> None:
        """
        Efface tous les résultats de checksums.
        Args:
            None
        Returns:
            None
        """
        for key in self.results:
            self.results[key].clear()
        logger.debug("Résultats effacés.")

__all__ = []