"""
Calculatrice avancée style collégien pour CrazyTerm.
Fonctions : +, -, ×, ÷, %, racine carrée, puissance, pi, parenthèses, effacer, clavier, etc.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
import math

class ToolCalculator(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculatrice avancée")
        self.setFixedSize(340, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFixedHeight(40)
        layout.addWidget(self.display)

        buttons = [
            ['7', '8', '9', '/', '√', 'C'],
            ['4', '5', '6', '*', '^', '⌫'],
            ['1', '2', '3', '-', '(', ')'],
            ['0', '.', '%', '+', 'π', '=']
        ]
        grid = QGridLayout()
        for row, row_vals in enumerate(buttons):
            for col, val in enumerate(row_vals):
                btn = QPushButton(val)
                btn.setFixedSize(50, 40)
                btn.clicked.connect(lambda checked, v=val: self.on_button(v))
                grid.addWidget(btn, row, col)
        layout.addLayout(grid)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.on_button('=')
        elif key == Qt.Key.Key_Backspace:
            self.on_button('⌫')
        elif key == Qt.Key.Key_Delete:
            self.on_button('C')
        else:
            text = event.text()
            if text in '0123456789.+-*/^()%':
                self.display.setText(self.display.text() + text)
            elif text == ',':
                self.display.setText(self.display.text() + '.')
            elif text == 'p':
                self.display.setText(self.display.text() + 'π')

    def on_button(self, value):
        if value == 'C':
            self.display.clear()
        elif value == '⌫':
            self.display.setText(self.display.text()[:-1])
        elif value == '=':
            try:
                expr = self.display.text().replace('π', str(math.pi)).replace('√', 'math.sqrt').replace('^', '**')
                # Sécurité : n'autorise que les caractères mathématiques
                allowed = '0123456789+-*/().% mathsqrtpi'
                if not all(c in allowed or c.isspace() for c in expr):
                    self.display.setText('Erreur')
                    return
                # Remplace % par /100 si utilisé comme opérateur
                expr = self._replace_percent(expr)
                result = str(eval(expr, {"__builtins__": None, "math": math}))
                self.display.setText(result)
            except Exception:
                self.display.setText('Erreur')
        elif value == 'π':
            self.display.setText(self.display.text() + 'π')
        elif value == '√':
            self.display.setText(self.display.text() + '√(')
        else:
            self.display.setText(self.display.text() + value)

    def _replace_percent(self, expr):
        # Remplace a%b par (a/100*b) si % est utilisé comme opérateur
        import re
        return re.sub(r'(\d+(?:\.\d+)?)%([\d(])', r'(\1/100*\2)', expr)

__all__ = ["ToolCalculator"]
