import logging
from typing import List, Any
from PyQt5.QtGui import QTextCharFormat, QColor

logger = logging.getLogger("CrazySerialTerm.TerminalBuffer")

class TerminalBufferManager:
    """
    Gère le buffer, le flush, la mémoire et les couleurs du terminal.
    """
    def __init__(self, terminal_output, max_chars=30000, theme='sombre'):
        self.terminal_output = terminal_output
        self._color_buffer: List[str] = []
        self._text_format_cache = {}
        self._pending_text_buffer: List[Any] = []
        self._max_terminal_chars = max_chars
        self.current_theme = theme
        self._cursor_pool = None
        self._last_cursor_position = 0
        self._object_creation_count = 0
        self._history: List[dict[str, str]] = []  # Buffer historique (texte + type)

    def append_text(self, text: str, color: str = 'text') -> None:
        if not text.endswith('\n'):
            text += '\n'
        self._pending_text_buffer.append((text, color))
        self._color_buffer.append(color)
        self._history.append({'text': text, 'color': color})  # Ajout à l'historique
        self.flush()  # Affichage immédiat

    def flush(self) -> None:
        if not self._pending_text_buffer or not self.terminal_output:
            return
        try:
            if not self._cursor_pool:
                self._cursor_pool = self.terminal_output.textCursor()
            cursor = self._cursor_pool
            cursor.movePosition(cursor.End)
            cursor.beginEditBlock()
            
            # N'utilise PAS de QTextCharFormat - laisse la palette globale agir
            for text, color in self._pending_text_buffer:
                cursor.insertText(text)
                self._object_creation_count += 1
            
            cursor.endEditBlock()
            self._last_cursor_position = cursor.position()
            self.terminal_output.setTextCursor(cursor)
            self.terminal_output.ensureCursorVisible()
            self._pending_text_buffer.clear()
            self._color_buffer.clear()
        except Exception as e:
            logger.error(f"Erreur dans flush: {e}")
            self._pending_text_buffer.clear()
            self._color_buffer.clear()

    def get_cached_format(self, color: str) -> QTextCharFormat:
        # Utilise la couleur du thème courant pour chaque type de message
        from interface.theme_manager import get_theme_terminal_colors
        theme_colors = get_theme_terminal_colors(self.current_theme)
        cache_key = f"{self.current_theme}_{color}"
        if cache_key not in self._text_format_cache:
            format_obj = QTextCharFormat()
            # Utilise la couleur du thème si connue, sinon blanc/noir par défaut
            if color in theme_colors:
                format_obj.setForeground(theme_colors[color])
            else:
                # fallback
                if self.current_theme == 'clair':
                    format_obj.setForeground(QColor(0, 0, 0))
                elif self.current_theme == 'hacker':
                    format_obj.setForeground(QColor(0, 255, 0))
                else:
                    format_obj.setForeground(QColor(255, 255, 255))
            self._text_format_cache[cache_key] = format_obj
        return self._text_format_cache[cache_key]

    def clear(self):
        if self.terminal_output:
            self.terminal_output.clear()
        self._pending_text_buffer.clear()
        self._color_buffer.clear()
        self._text_format_cache.clear()
        self._cursor_pool = None
        self._last_cursor_position = 0
        self._object_creation_count = 0

    def aggressive_cleanup(self):
        self.clear()
        if self.terminal_output:
            self.terminal_output.clear()
            self._add_single_text("[Système] Nettoyage mémoire automatique effectué\n", 'system')

    def replay_history(self):
        """
        Pas besoin de réafficher l'historique - le texte change automatiquement
        de couleur grâce à la palette globale de l'application.
        """
        # Plus besoin de vider et réafficher - la palette globale s'occupe de tout
        pass

    def _add_single_text(self, text: str, color: str = 'text'):
        """
        Ajoute du texte simple sans format - laisse la palette globale agir.
        """
        if not self.terminal_output:
            return
        cursor = self.terminal_output.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.terminal_output.setTextCursor(cursor)
        self.terminal_output.ensureCursorVisible()

    def set_theme(self, theme_name: str):
        """
        Met à jour le thème courant du buffer.
        Le changement de couleur se fait automatiquement via la palette globale.
        """
        self.current_theme = theme_name
        # Plus besoin de vider le cache ou de réafficher - la palette s'occupe de tout
