#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module : memory_optimizer.py

Outil interne CrazyTerm : Optimisation mémoire (non natif, chargé dynamiquement)

Rôle :
    Fournit des fonctions et classes pour améliorer la gestion mémoire, optimiser l’utilisation des ressources
    et prévenir les fuites dans l’application CrazyTerm.

Fonctionnalités principales :
    - Pool d’objets réutilisables
    - Nettoyage automatique via garbage collector
    - Surveillance mémoire et outils de diagnostic
    - Intégration avec les composants PyQt5

Dépendances :
    - gc
    - weakref
    - threading
    - PyQt5
    - logging

Utilisation :
    Ce module est utilisé par les composants cœur et l’interface pour garantir la stabilité mémoire.

Auteur :
    Projet CrazyTerm (2025) Manu
"""


from __future__ import annotations

import gc
import weakref
import threading
from typing import Dict, List, Optional, Set, Any, Callable
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
from PyQt5.QtWidgets import QTextEdit
import logging

# Initialize logger
logger = logging.getLogger("UltraMemoryManager")

class ObjectPool:
    """A pool of reusable objects to minimize allocations."""

    def __init__(self, max_size: int = 10) -> None:
        """
        Initialize the object pool.

        Args:
            max_size (int): Maximum size of the pool.
        """
        self._pool: List[Any] = []
        self._max_size: int = max_size
        self._lock: threading.Lock = threading.Lock()

    def acquire(self, factory_func: Callable[[], Any]) -> Any:
        """
        Acquire an object from the pool or create a new one.

        Args:
            factory_func (Callable[[], Any]): Function to create a new object.

        Returns:
            Any: Object from the pool or a new object.
        """
        with self._lock:
            if self._pool:
                return self._pool.pop()
            return factory_func()

    def release(self, obj: Any) -> None:
        """
        Return an object to the pool.

        Args:
            obj (Any): Object to return to the pool.
        """
        with self._lock:
            if len(self._pool) < self._max_size:
                if hasattr(obj, 'clear'):
                    obj.clear()
                self._pool.append(obj)

    def clear(self) -> None:
        """Clear the pool completely."""
        with self._lock:
            self._pool.clear()

class UltraMemoryManager(QObject):
    """Ultra-optimized memory manager with proactive monitoring and aggressive cleanup."""

    memory_warning = pyqtSignal(int)

    def __init__(self) -> None:
        """
        Initialize the memory manager, pools, cache, and cleanup timer.
        """
        super().__init__()
        try:
            self._cursor_pool: ObjectPool = ObjectPool(max_size=5)
            self._format_pool: ObjectPool = ObjectPool(max_size=10)
            self._format_cache: Dict[str, QTextCharFormat] = {}
            self._weak_refs: Set[weakref.ref] = set()
            self._text_buffer: List[str] = []
            self._buffer_lock: threading.Lock = threading.Lock()
            self._max_buffer_size: int = 50
            self._object_count: int = 0
            self._peak_object_count: int = 0
            self._cleanup_counter: int = 0
            self._cleanup_timer: QTimer = QTimer()
            self._cleanup_timer.timeout.connect(self._aggressive_cleanup)
            self._cleanup_timer.start(5000)
            self._tracked_objects: Set[weakref.ref] = set()
            logger.info("UltraMemoryManager initialized")
        except Exception as e:
            logger.error(f"Error initializing UltraMemoryManager: {e}")

    def get_cached_format(self, color: str, bold: bool = False) -> QTextCharFormat:
        """
        Retrieve a format from the cache or create it (with pool).

        Args:
            color (str): Text color (name or hexadecimal).
            bold (bool): True for bold text.

        Returns:
            QTextCharFormat: PyQt text format.
        """
        cache_key = f"{color}_{bold}"
        if cache_key not in self._format_cache:
            fmt: QTextCharFormat = self._format_pool.acquire(QTextCharFormat)
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(700)
            self._format_cache[cache_key] = fmt
            self._object_count += 1
        return self._format_cache[cache_key]

    def get_cursor(self, text_edit: QTextEdit) -> QTextCursor:
        """
        Retrieve a cursor from the pool.

        Args:
            text_edit (QTextEdit): Target widget.

        Returns:
            QTextCursor: PyQt cursor.
        """
        cursor: QTextCursor = self._cursor_pool.acquire(lambda: text_edit.textCursor())
        cursor.movePosition(QTextCursor.End)
        return cursor

    def release_cursor(self, cursor: QTextCursor) -> None:
        """
        Return a cursor to the pool.

        Args:
            cursor (QTextCursor): Cursor to return.
        """
        self._cursor_pool.release(cursor)

    def add_to_buffer(self, text: str) -> bool:
        """
        Add text to the buffer. Return True if a flush is needed.

        Args:
            text (str): Text to add.

        Returns:
            bool: True if the buffer needs to be flushed.
        """
        with self._buffer_lock:
            self._text_buffer.append(text)
            return len(self._text_buffer) >= self._max_buffer_size

    def flush_buffer(self, text_edit: QTextEdit) -> None:
        """
        Flush the buffer to the terminal with memory optimization.

        Args:
            text_edit (QTextEdit): Target widget.
        """
        with self._buffer_lock:
            if not self._text_buffer:
                return
            combined_text: str = ''.join(self._text_buffer)
            self._text_buffer.clear()
            cursor: QTextCursor = self.get_cursor(text_edit)
            cursor.insertText(combined_text)
            self.release_cursor(cursor)
            if self._object_count > 30:
                self._immediate_cleanup()

    def track_object(self, obj: Any) -> None:
        """
        Track an object with a weak reference for automatic cleanup.

        Args:
            obj (Any): Object to track.
        """
        def cleanup_callback(ref: weakref.ReferenceType[Any]) -> None:
            """
            Internal callback for automatic cleanup of the referenced object.

            Args:
                ref (weakref.ReferenceType[Any]): Weak reference to the object.
            """
            self._tracked_objects.discard(ref)
            self._object_count -= 1

        ref: weakref.ReferenceType[Any] = weakref.ref(obj, cleanup_callback)
        self._tracked_objects.add(ref)
        self._object_count += 1
        if self._object_count > self._peak_object_count:
            self._peak_object_count = self._object_count

    def _aggressive_cleanup(self) -> None:
        """Periodic aggressive cleanup."""
        try:
            self._cleanup_counter += 1
            if len(self._format_cache) > 5:
                keys = list(self._format_cache.keys())
                for key in keys[:-3]:
                    fmt = self._format_cache.pop(key)
                    self._format_pool.release(fmt)
            dead_refs = {ref for ref in self._tracked_objects if ref() is None}
            self._tracked_objects -= dead_refs
            if self._cleanup_counter % 3 == 0:
                collected: int = gc.collect()
                if collected > 0:
                    logger.debug(f"GC collected: {collected} objects")
            if self._object_count > 40:
                self.memory_warning.emit(self._object_count)
                self._immediate_cleanup()
        except Exception as e:
            logger.error(f"Error during aggressive cleanup: {e}")

    def _immediate_cleanup(self) -> None:
        """Immediate and aggressive cleanup."""
        try:
            logger.warning(f"Immediate cleanup: {self._object_count} objects")
            for fmt in self._format_cache.values():
                self._format_pool.release(fmt)
            self._format_cache.clear()
            for _ in range(3):
                gc.collect()
            self._object_count = max(0, self._object_count - 20)
        except Exception as e:
            logger.error(f"Error during immediate cleanup: {e}")

    def get_memory_stats(self) -> Dict[str, int]:
        """
        Return memory statistics.

        Returns:
            Dict[str, int]: Current memory statistics.
        """
        return {
            'current_objects': self._object_count,
            'peak_objects': self._peak_object_count,
            'cache_size': len(self._format_cache),
            'buffer_size': len(self._text_buffer),
            'tracked_objects': len(self._tracked_objects)
        }

    def emergency_cleanup(self) -> None:
        """Complete emergency cleanup."""
        try:
            logger.critical("EMERGENCY CLEANUP ACTIVATED")
            with self._buffer_lock:
                self._text_buffer.clear()
            self._cursor_pool.clear()
            self._format_pool.clear()
            self._format_cache.clear()
            self._tracked_objects.clear()
            self._object_count = 0
            for _ in range(5):
                gc.collect()
            logger.info("Emergency cleanup completed")
        except Exception as e:
            logger.error(f"Error during emergency cleanup: {e}")

# Global instance
_ultra_memory_manager: Optional[UltraMemoryManager] = None

def get_ultra_memory_manager() -> UltraMemoryManager:
    """
    Return the global instance of the memory manager.

    Returns:
        UltraMemoryManager: Global instance of the memory manager.

    Raises:
        Exception: If initialization fails.
    """
    global _ultra_memory_manager
    try:
        if _ultra_memory_manager is None:
            _ultra_memory_manager = UltraMemoryManager()
        return _ultra_memory_manager
    except Exception as e:
        logger.error(f"Error creating global UltraMemoryManager instance: {e}")
        raise

__all__ = []
