"""
Module tool_converter pour CrazyTerm.

Ce module contient la classe ToolConverter qui fournit des fonctionnalités
de conversion de données pour l'application CrazyTerm.
"""

import logging
from typing import Union, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ToolConverter:
    """
    Outil de conversion de données pour CrazyTerm.
    
    Cette classe fournit des fonctionnalités de conversion de données
    incluant les conversions numériques, de bases et d'unités.
    
    Attributes:
        _history (List[str]): Historique des conversions
        
    Methods:
        convert_base: Convertit entre bases numériques
        convert_temperature: Convertit les températures
        convert_length: Convertit les longueurs
        
    Examples:
        >>> converter = ToolConverter()
        >>> result = converter.convert_base("255", 10, 16)
        >>> print(result)
        FF
        
    Note:
        Cette classe utilise les algorithmes standards de conversion.
    """
    
    def __init__(self) -> None:
        """Initialise l'outil de conversion."""
        self._history: list = []
        self.logger = logger
        self.logger.info("ToolConverter initialisé")
    
    def convert_base(self, number: str, from_base: int, to_base: int) -> str:
        """
        Convertit un nombre d'une base à une autre.
        
        Args:
            number: Nombre à convertir
            from_base: Base source
            to_base: Base destination
            
        Returns:
            str: Nombre converti
        """
        try:
            # Conversion vers décimal puis vers base cible
            decimal_value = int(number, from_base)
            
            if to_base == 10:
                result = str(decimal_value)
            elif to_base == 2:
                result = bin(decimal_value)[2:]
            elif to_base == 8:
                result = oct(decimal_value)[2:]
            elif to_base == 16:
                result = hex(decimal_value)[2:].upper()
            else:
                # Base générique
                result = self._convert_to_base(decimal_value, to_base)
            
            self._history.append(f"Base {from_base} -> {to_base}: {number} = {result}")
            self.logger.debug(f"Conversion base: {number} ({from_base}) -> {result} ({to_base})")
            return result
            
        except Exception as e:
            error_msg = f"Erreur conversion base: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def _convert_to_base(self, number: int, base: int) -> str:
        """Convertit un nombre vers une base arbitraire."""
        if number == 0:
            return "0"
        
        digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = ""
        
        while number > 0:
            result = digits[number % base] + result
            number //= base
        
        return result
    
    def convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """
        Convertit une température d'une unité à une autre.
        
        Args:
            value: Valeur à convertir
            from_unit: Unité source (C, F, K)
            to_unit: Unité destination (C, F, K)
            
        Returns:
            float: Valeur convertie
        """
        try:
            # Conversion vers Celsius
            if from_unit.upper() == 'F':
                celsius = (value - 32) * 5/9
            elif from_unit.upper() == 'K':
                celsius = value - 273.15
            else:
                celsius = value
            
            # Conversion depuis Celsius
            if to_unit.upper() == 'F':
                result = celsius * 9/5 + 32
            elif to_unit.upper() == 'K':
                result = celsius + 273.15
            else:
                result = celsius
            
            self._history.append(f"Température {from_unit} -> {to_unit}: {value} = {result}")
            self.logger.debug(f"Conversion température: {value}°{from_unit} -> {result}°{to_unit}")
            return round(result, 2)
            
        except Exception as e:
            error_msg = f"Erreur conversion température: {str(e)}"
            self.logger.error(error_msg)
            return 0.0
    
    def convert_length(self, value: float, from_unit: str, to_unit: str) -> float:
        """
        Convertit une longueur d'une unité à une autre.
        
        Args:
            value: Valeur à convertir
            from_unit: Unité source (mm, cm, m, km, in, ft)
            to_unit: Unité destination
            
        Returns:
            float: Valeur convertie
        """
        try:
            # Facteurs de conversion vers mètres
            to_meters = {
                'mm': 0.001,
                'cm': 0.01,
                'm': 1.0,
                'km': 1000.0,
                'in': 0.0254,
                'ft': 0.3048
            }
            
            # Conversion vers mètres puis vers unité cible
            meters = value * to_meters.get(from_unit.lower(), 1.0)
            result = meters / to_meters.get(to_unit.lower(), 1.0)
            
            self._history.append(f"Longueur {from_unit} -> {to_unit}: {value} = {result}")
            self.logger.debug(f"Conversion longueur: {value} {from_unit} -> {result} {to_unit}")
            return round(result, 6)
            
        except Exception as e:
            error_msg = f"Erreur conversion longueur: {str(e)}"
            self.logger.error(error_msg)
            return 0.0
    
    def get_history(self) -> list:
        """Retourne l'historique des conversions."""
        return self._history.copy()
    
    def clear_history(self) -> None:
        """Efface l'historique des conversions."""
        self._history.clear()
        self.logger.debug("Historique effacé")
    
    def get_info(self) -> Dict[str, Any]:
        """Retourne les informations de l'outil."""
        return {
            'name': 'ToolConverter',
            'version': '1.0.0',
            'history_count': len(self._history),
            'available_conversions': [
                'Base numérique', 'Température', 'Longueur'
            ]
        }
    
    def __str__(self) -> str:
        """Représentation string de l'outil."""
        return f"ToolConverter(history={len(self._history)} items)"
    
    def __repr__(self) -> str:
        """Représentation détaillée de l'outil."""
        return f"ToolConverter(_history={len(self._history)} items)"
