"""
Module tool_checksum pour CrazyTerm.

Ce module contient la classe ToolChecksum qui fournit des fonctionnalités
de calcul de checksum et de hachage pour l'application CrazyTerm.
"""

import logging
import hashlib
import zlib
from typing import Union, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ToolChecksum:
    """
    Outil de calcul de checksum et de hachage pour CrazyTerm.
    
    Cette classe fournit des fonctionnalités de calcul de checksum et de hachage
    incluant MD5, SHA1, SHA256, SHA512 et CRC32.
    
    Attributes:
        _history (List[str]): Historique des calculs
        
    Methods:
        calculate_md5: Calcule le hash MD5
        calculate_sha1: Calcule le hash SHA1
        calculate_sha256: Calcule le hash SHA256
        calculate_crc32: Calcule le checksum CRC32
        
    Examples:
        >>> checksum = ToolChecksum()
        >>> result = checksum.calculate_md5("Hello World")
        >>> print(result)
        b10a8db164e0754105b7a99be72e3fe5
        
    Note:
        Cette classe utilise les algorithmes standards de hachage.
    """
    
    def __init__(self) -> None:
        """Initialise l'outil checksum."""
        self._history: list = []
        self.logger = logger
        self.logger.info("ToolChecksum initialisé")
    
    def calculate_md5(self, data: str) -> str:
        """
        Calcule le hash MD5 d'une chaîne.
        
        Args:
            data: Données à hasher
            
        Returns:
            str: Hash MD5 en hexadécimal
        """
        try:
            md5_hash = hashlib.md5(data.encode()).hexdigest()
            self._history.append(f"MD5({data}) = {md5_hash}")
            self.logger.debug(f"MD5 calculé pour: {data[:20]}...")
            return md5_hash
        except Exception as e:
            error_msg = f"Erreur MD5: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def calculate_sha1(self, data: str) -> str:
        """
        Calcule le hash SHA1 d'une chaîne.
        
        Args:
            data: Données à hasher
            
        Returns:
            str: Hash SHA1 en hexadécimal
        """
        try:
            sha1_hash = hashlib.sha1(data.encode()).hexdigest()
            self._history.append(f"SHA1({data}) = {sha1_hash}")
            self.logger.debug(f"SHA1 calculé pour: {data[:20]}...")
            return sha1_hash
        except Exception as e:
            error_msg = f"Erreur SHA1: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def calculate_sha256(self, data: str) -> str:
        """
        Calcule le hash SHA256 d'une chaîne.
        
        Args:
            data: Données à hasher
            
        Returns:
            str: Hash SHA256 en hexadécimal
        """
        try:
            sha256_hash = hashlib.sha256(data.encode()).hexdigest()
            self._history.append(f"SHA256({data}) = {sha256_hash}")
            self.logger.debug(f"SHA256 calculé pour: {data[:20]}...")
            return sha256_hash
        except Exception as e:
            error_msg = f"Erreur SHA256: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def calculate_crc32(self, data: str) -> str:
        """
        Calcule le checksum CRC32 d'une chaîne.
        
        Args:
            data: Données à hasher
            
        Returns:
            str: Checksum CRC32 en hexadécimal
        """
        try:
            crc32_value = zlib.crc32(data.encode()) & 0xffffffff
            crc32_hex = format(crc32_value, '08x')
            self._history.append(f"CRC32({data}) = {crc32_hex}")
            self.logger.debug(f"CRC32 calculé pour: {data[:20]}...")
            return crc32_hex
        except Exception as e:
            error_msg = f"Erreur CRC32: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def get_history(self) -> list:
        """Retourne l'historique des calculs."""
        return self._history.copy()
    
    def clear_history(self) -> None:
        """Efface l'historique des calculs."""
        self._history.clear()
        self.logger.debug("Historique effacé")
    
    def get_info(self) -> Dict[str, Any]:
        """Retourne les informations de l'outil."""
        return {
            'name': 'ToolChecksum',
            'version': '1.0.0',
            'history_count': len(self._history),
            'available_algorithms': [
                'MD5', 'SHA1', 'SHA256', 'CRC32'
            ]
        }
    
    def __str__(self) -> str:
        """Représentation string de l'outil."""
        return f"ToolChecksum(history={len(self._history)} items)"
    
    def __repr__(self) -> str:
        """Représentation détaillée de l'outil."""
        return f"ToolChecksum(_history={len(self._history)} items)"
