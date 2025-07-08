from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QGroupBox)

class DataConverter(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Convertisseur de Données (ASCII/HEX)")
        self.resize(400, 200)

        layout = QVBoxLayout(self)

        # Zone d'entrée
        inputGroup = QGroupBox("Données d'entrée")
        inputLayout = QVBoxLayout()
        self.inputText = QTextEdit()
        self.inputText.setPlaceholderText("Entrez les données à convertir...")
        inputLayout.addWidget(self.inputText)
        inputGroup.setLayout(inputLayout)
        layout.addWidget(inputGroup)

        # Zone de sortie
        outputGroup = QGroupBox("Données converties")
        outputLayout = QVBoxLayout()
        self.outputText = QTextEdit()
        self.outputText.setReadOnly(True)
        outputLayout.addWidget(self.outputText)
        outputGroup.setLayout(outputLayout)
        layout.addWidget(outputGroup)

        # Boutons
        buttonLayout = QHBoxLayout()
        self.toHexBtn = QPushButton("Convertir en HEX")
        self.toHexBtn.clicked.connect(self.convertToHex)
        buttonLayout.addWidget(self.toHexBtn)

        self.toAsciiBtn = QPushButton("Convertir en ASCII")
        self.toAsciiBtn.clicked.connect(self.convertToAscii)
        buttonLayout.addWidget(self.toAsciiBtn)

        closeBtn = QPushButton("Fermer")
        closeBtn.clicked.connect(self.accept)
        buttonLayout.addWidget(closeBtn)

        layout.addLayout(buttonLayout)

    def convertToHex(self): 
        try:
            text = self.inputText.toPlainText()
            if not text:
                self.outputText.setText("Aucune donnée à convertir")
                return
            self.outputText.setText(' '.join(f'{ord(c):02X}' for c in text))
        except Exception as e:
            self.outputText.setText(f"Erreur lors de la conversion: {str(e)}")
            
    def convertToAscii(self):
        try: 
            text = self.inputText.toPlainText().replace(' ', '').replace('\n', '').replace('\t', '')
            if not text:
                self.outputText.setText("Aucune donnée à convertir")
                return
            if len(text) % 2 != 0:
                self.outputText.setText("Erreur : nombre impair de caractères HEX")
                return
            self.outputText.setText(bytes.fromhex(text).decode('utf-8', errors='replace'))
        except ValueError: 
            self.outputText.setText("Erreur : données HEX invalides")
        except Exception as e:
            self.outputText.setText(f"Erreur lors de la conversion: {str(e)}")