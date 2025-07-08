"""
Gestionnaire de mémoire ultra-optimisé pour CrazySerialTerm
Objectif: A        logger.info("UltraMemoryManager initialisé")
    
    def get_cursor(self, text_edit: QTextEdit) -> QTextCursor:obustesse avec une fuite mémoire quasi-nulle (<50 objets Qt)
"""

import gc
import threading
from typing import Dict, List, Any
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QTextCursor, QTextCharFormat
from PyQt5.QtWidgets import QTextEdit
import logging

logger = logging.getLogger("UltraMemoryManager")

class ObjectPool:
    """Pool d'objets réutilisables pour minimiser les allocations."""
    
    def __init__(self, max_size: int = 10):
        self._pool: List[Any] = []
        self._max_size = max_size
        self._lock = threading.Lock()
    
    def acquire(self, factory_func):
        """Acquiert un objet du pool ou en crée un nouveau."""
        with self._lock:
            if self._pool:
                return self._pool.pop()
            return factory_func()
    
    def release(self, obj):
        """Remet un objet dans le pool."""
        with self._lock:
            if len(self._pool) < self._max_size:
                # Reset de l'objet si possible
                if hasattr(obj, 'clear'):
                    obj.clear()
                self._pool.append(obj)

class UltraMemoryManager(QObject):
    """
    Gestionnaire de mémoire ultra-optimisé avec surveillance proactive
    et nettoyage agressif pour minimiser les fuites mémoire.
    """
    
    memory_warning = pyqtSignal(int)  # Signal quand la mémoire dépasse un seuil
    
    def __init__(self):
        super().__init__()
        
        # Pools d'objets réutilisables
        self._cursor_pool = ObjectPool(max_size=5)
        self._format_pool = ObjectPool(max_size=10)
        
        # Cache ultra-optimisé
        self._format_cache: Dict[str, QTextCharFormat] = {}
        
        # Buffer de texte avec limitation stricte
        self._text_buffer: List[str] = []
        self._buffer_lock = threading.Lock()
        self._max_buffer_size = 50  # Très petit buffer
        
        # Surveillance mémoire
        self._object_count = 0
        self._peak_object_count = 0
        self._cleanup_counter = 0
        
        # Timer de nettoyage agressif
        self._cleanup_timer = QTimer()
        self._cleanup_timer.timeout.connect(self._aggressive_cleanup)
        self._cleanup_timer.start(5000)  # Nettoyage toutes les 5 secondes
        
        logger.info("UltraMemoryManager initialisé")
    
    def get_cached_format(self, color: str, bold: bool = False) -> QTextCharFormat:
        """Récupère un format depuis le cache ou le crée (avec pool)."""
        cache_key = f"{color}_{bold}"
        
        if cache_key not in self._format_cache:
            # Utiliser le pool pour créer le format
            fmt = self._format_pool.acquire(QTextCharFormat)
            fmt.setForeground(color)
            if bold:
                fmt.setFontWeight(700)
            
            self._format_cache[cache_key] = fmt
            self._object_count += 1
        
        return self._format_cache[cache_key]
    
    def get_cursor(self, text_edit: QTextEdit) -> QTextCursor:
        """Récupère un curseur depuis le pool."""
        cursor = self._cursor_pool.acquire(lambda: text_edit.textCursor())
        cursor.movePosition(QTextCursor.End)
        return cursor
    
    def release_cursor(self, cursor: QTextCursor):
        """Remet un curseur dans le pool."""
        self._cursor_pool.release(cursor)
    
    def add_to_buffer(self, text: str) -> bool:
        """Ajoute du texte au buffer. Retourne True si flush nécessaire."""
        with self._buffer_lock:
            self._text_buffer.append(text)
            return len(self._text_buffer) >= self._max_buffer_size
    
    def flush_buffer(self, text_edit: QTextEdit):
        """Flush le buffer vers le terminal avec optimisation mémoire."""
        with self._buffer_lock:
            if not self._text_buffer:
                return
            
            # Combine tout le texte en une seule opération
            combined_text = ''.join(self._text_buffer)
            self._text_buffer.clear()
            
            # Utilise un seul curseur pour tout
            cursor = self.get_cursor(text_edit)
            cursor.insertText(combined_text)
            self.release_cursor(cursor)
            
            # Force le nettoyage si nécessaire
            if self._object_count > 30:
                self._immediate_cleanup()
    
    def _aggressive_cleanup(self):
        """Nettoyage agressif périodique."""
        self._cleanup_counter += 1
        
        # Nettoyage du cache si trop gros
        if len(self._format_cache) > 5:
            # Garde seulement les 3 plus récents
            keys = list(self._format_cache.keys())
            for key in keys[:-3]:
                fmt = self._format_cache.pop(key)
                self._format_pool.release(fmt)
        
        # Garbage collection agressif
        if self._cleanup_counter % 3 == 0:  # Toutes les 15 secondes
            collected = gc.collect()
            if collected > 0:
                logger.debug(f"GC collecté: {collected} objets")
        
        # Warning si trop d'objets
        if self._object_count > 40:
            self.memory_warning.emit(self._object_count)
            self._immediate_cleanup()
    
    def _immediate_cleanup(self):
        """Nettoyage immédiat et agressif."""
        logger.warning(f"Nettoyage immédiat: {self._object_count} objets")
        
        # Vide complètement le cache
        for fmt in self._format_cache.values():
            self._format_pool.release(fmt)
        self._format_cache.clear()
        
        # Force plusieurs GC
        for _ in range(3):
            gc.collect()
        
        # Reset les compteurs
        self._object_count = max(0, self._object_count - 20)
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Retourne les statistiques mémoire."""
        return {
            'current_objects': self._object_count,
            'peak_objects': self._peak_object_count,
            'cache_size': len(self._format_cache),
            'buffer_size': len(self._text_buffer)
        }
    
    def emergency_cleanup(self):
        """Nettoyage d'urgence complet."""
        logger.critical("NETTOYAGE D'URGENCE ACTIVÉ")
        
        with self._buffer_lock:
            self._text_buffer.clear()
        
        # Vide tous les pools
        try:
            self._cursor_pool._pool.clear()
            self._format_pool._pool.clear()
        except:
            pass
        
        # Vide le cache
        self._format_cache.clear()
        
        # Reset compteurs
        self._object_count = 0
        
        # GC ultra-agressif
        for _ in range(5):
            gc.collect()
        
        logger.info("Nettoyage d'urgence terminé")

# Instance globale
_ultra_memory_manager = None

def get_ultra_memory_manager() -> UltraMemoryManager:
    """Retourne l'instance globale du gestionnaire mémoire."""
    global _ultra_memory_manager
    if _ultra_memory_manager is None:
        _ultra_memory_manager = UltraMemoryManager()
    return _ultra_memory_manager
