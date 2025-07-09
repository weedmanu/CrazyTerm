"""
Module de communication série pour CrazyTerm.
Gère l'envoi et la réception de données via les ports série.
"""

from __future__ import annotations

import serial
import serial.tools.list_ports
from datetime import datetime
from typing import List, Dict, Any, Optional, Deque
import logging
from collections import deque

from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer, QMutex, QMutexLocker

from system.custom_exceptions import (
    SerialPortException, 
    DataTransmissionException
)
from system.error_handling import retry_with_backoff, CircuitBreaker

logger = logging.getLogger("CrazySerialTerm.SerialManager")

class SerialReaderThread(QThread):
    """Thread de lecture série robuste avec gestion d'erreurs avancée."""
    
    data_received = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)
    connection_lost = pyqtSignal()
    
    def __init__(self, serial_port: Optional[serial.Serial]) -> None:
        """
        Initialise le thread de lecture série.
        Args:
            serial_port (Optional[serial.Serial]): Instance de serial.Serial à utiliser pour la lecture.
        Returns:
            None
        """
        super().__init__()
        self.serial_port: Optional[serial.Serial] = serial_port
        self.running: bool = False
        self.buffer: Deque[bytes] = deque(maxlen=10000)  # Buffer circulaire limité
        self.read_timeout: float = 0.1
        self.error_count: int = 0
        self.max_errors: int = 5  # Réduit pour une détection plus rapide des déconnexions
        
    def run(self) -> None:
        """
        Boucle principale de lecture série avec gestion d'erreurs et signaux Qt.
        Returns:
            None
        """
        self.running = True
        consecutive_errors: int = 0
        logger.debug("Thread de lecture série démarré")
        try:
            while self.running:
                try:
                    if not self.serial_port or not self.serial_port.is_open:
                        logger.warning("Port série fermé, arrêt du thread")
                        break
                    # Lecture non-bloquante avec timeout
                    if self.serial_port.in_waiting > 0:
                        data: bytes = self.serial_port.read(min(self.serial_port.in_waiting, 4096))
                        if data:
                            self.data_received.emit(data)
                            consecutive_errors = 0  # Reset en cas de succès
                    else:
                        # Petite pause pour éviter la surcharge CPU
                        self.msleep(10)
                except (serial.SerialException, OSError, IOError, PermissionError) as e:
                    consecutive_errors += 1
                    # Détection spécifique des déconnexions USB
                    if isinstance(e, PermissionError) and hasattr(e, 'errno') and e.errno == 22:
                        logger.warning(f"Déconnexion USB détectée: {e}")
                        self.error_occurred.emit("Périphérique USB déconnecté")
                        self.connection_lost.emit()
                        break
                    elif "ClearCommError failed" in str(e):
                        logger.warning(f"Erreur de communication USB: {e}")
                        self.error_occurred.emit("Erreur de communication USB - Vérifiez la connexion")
                        self.connection_lost.emit()
                        break
                    elif consecutive_errors >= 3 and any(keyword in str(e).lower() for keyword in 
                                                       ['permission denied', 'device not ready', 'no such device']):
                        logger.warning(f"Déconnexion détectée: {e}")
                        self.error_occurred.emit("Périphérique déconnecté")
                        self.connection_lost.emit()
                        break
                    logger.warning(f"Erreur de lecture série (#{consecutive_errors}): {e}")
                    if consecutive_errors >= self.max_errors:
                        self.error_occurred.emit(f"Trop d'erreurs consécutives: {e}")
                        self.connection_lost.emit()
                        break
                    # Pause progressive en cas d'erreurs (plus courte pour les erreurs USB)
                    if isinstance(e, PermissionError):
                        self.msleep(50)  # Pause courte pour les erreurs USB
                    else:
                        self.msleep(min(100 * consecutive_errors, 5000))
                except Exception as e:
                    logger.error(f"Erreur inattendue dans le thread de lecture: {e}")
                    self.error_occurred.emit(f"Erreur critique: {e}")
                    break
        except Exception as e:
            logger.error(f"Erreur fatale dans le thread de lecture: {e}")
            self.error_occurred.emit(f"Erreur fatale: {e}")
        finally:
            logger.debug("Thread de lecture série terminé")
            
    def stop(self) -> None:
        """
        Arrête le thread proprement.
        Returns:
            None
        """
        self.running = False
        
class RobustSerialManager(QObject):
    """
    Gestionnaire série robuste avec gestion d'erreurs avancée,
    circuit breaker, retry automatique, statistiques et signaux thread-safe.
    """
    
    # Signaux thread-safe
    data_received = pyqtSignal(bytes)
    connection_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    statistics_updated = pyqtSignal(dict)
    
    def __init__(self) -> None:
        """
        Initialise le gestionnaire série robuste et ses timers/statistiques.
        Returns:
            None
        """
        super().__init__()
        # État de connexion
        self.serial_port: Optional[serial.Serial] = None
        self.reader_thread: Optional[SerialReaderThread] = None
        self.is_connected_flag: bool = False
        
        # Thread safety
        self.mutex: QMutex = QMutex()
        
        # Statistiques
        self.rx_bytes_count: int = 0
        self.tx_bytes_count: int = 0
        self.connection_start_time: Optional[datetime] = None
        
        # Robustesse
        self.circuit_breaker: CircuitBreaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30.0)
        self.last_error_time: Optional[datetime] = None
        self.error_count: int = 0
        
        # Timer pour les statistiques
        self.stats_timer: QTimer = QTimer()
        self.stats_timer.timeout.connect(self.emit_statistics)
        self.stats_timer.start(1000)  # Mise à jour chaque seconde
        
        # Timer de vérification de santé de la connexion
        self.health_timer: QTimer = QTimer()
        self.health_timer.timeout.connect(self.check_connection_health)
        self.health_timer.start(2000)  # Vérification toutes les 2 secondes
    
    @retry_with_backoff(max_retries=3, exceptions=(serial.SerialException, OSError))
    def get_available_ports(self) -> List[str]:
        """
        Liste les ports série disponibles avec retry automatique.
        Returns:
            List[str]: Liste des noms de ports disponibles.
        """
        try:
            ports: List[str] = [port.device for port in serial.tools.list_ports.comports()]
            logger.debug(f"Ports trouvés: {ports}")
            return ports
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des ports: {e}")
            raise SerialPortException(f"Impossible de lister les ports: {e}")

    def get_port_info(self, port_name: str) -> Dict[str, Any]:
        """
        Obtient les informations détaillées d'un port.
        Args:
            port_name (str): Nom du port à interroger.
        Returns:
            Dict[str, Any]: Dictionnaire d'informations sur le port.
        """
        try:
            for port in serial.tools.list_ports.comports():
                if port.device == port_name:
                    return {
                        "name": port.device,
                        "description": port.description,
                        "manufacturer": port.manufacturer,
                        "hwid": port.hwid,
                        "vid": port.vid,
                        "pid": port.pid,
                        "serial_number": port.serial_number,
                        "available": True
                    }
            return {"name": port_name, "description": "Port non trouvé", "available": False}
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos du port {port_name}: {e}")
            return {"name": port_name, "description": "Erreur", "available": False}

    def connect(self, port: str, **kwargs: Any) -> bool:
        """
        Connexion robuste avec validation et gestion d'erreurs.
        Args:
            port (str): Nom du port série à ouvrir.
            **kwargs (Any): Paramètres additionnels pour serial.Serial.
        Returns:
            bool: True si la connexion a réussi, False sinon.
        """
        with QMutexLocker(self.mutex):
            if self.is_connected_flag:
                self.disconnect_port()
            try:
                # Validation des paramètres
                if not port:
                    raise SerialPortException("Port invalide")
                params: Dict[str, Any] = {
                    'port': port,
                    'baudrate': 115200,
                    'bytesize': 8,
                    'parity': 'N',
                    'stopbits': 1,
                    'timeout': 0.1,
                    'write_timeout': 1.0,
                    'xonxoff': False,
                    'rtscts': False,
                    'dsrdtr': False
                }
                params.update(kwargs)
                self._validate_serial_params(params)
                def _connect() -> bool:
                    """
                    Fonction interne pour la connexion série réelle.
                    Returns:
                        bool: True si la connexion a réussi, False sinon.
                    """
                    return self._do_connect(params)
                result: bool = bool(self.circuit_breaker.call(_connect))
                if result:
                    self.connection_start_time = datetime.now()
                    self.rx_bytes_count = 0
                    self.tx_bytes_count = 0
                    self.is_connected_flag = True
                    self.connection_changed.emit(True)
                    logger.info(f"Connexion établie sur {port}")
                return result
            except Exception as e:
                error_msg = f"Échec de connexion sur {port}: {e}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False

    def _validate_serial_params(self, params: Dict[str, Any]) -> None:
        """
        Valide les paramètres de connexion série.
        Args:
            params (Dict[str, Any]): Dictionnaire de paramètres pour serial.Serial.
        Returns:
            None
        Raises:
            SerialPortException: en cas de paramètre invalide.
        """
        valid_baudrates: List[int] = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        valid_bytesizes: List[int] = [5, 6, 7, 8]
        valid_parities: List[str] = ['N', 'E', 'O', 'M', 'S']
        valid_stopbits: List[float] = [1, 1.5, 2]
        if params['baudrate'] not in valid_baudrates:
            raise SerialPortException(f"Baudrate invalide: {params['baudrate']}")
        if params['bytesize'] not in valid_bytesizes:
            raise SerialPortException(f"Bytesize invalide: {params['bytesize']}")
        if params['parity'] not in valid_parities:
            raise SerialPortException(f"Parité invalide: {params['parity']}")
        if params['stopbits'] not in valid_stopbits:
            raise SerialPortException(f"Stop bits invalides: {params['stopbits']}")

    def _do_connect(self, params: Dict[str, Any]) -> bool:
        """
        Effectue la connexion série réelle et démarre le thread de lecture.
        Args:
            params (Dict[str, Any]): Dictionnaire de paramètres pour serial.Serial.
        Returns:
            bool: True si la connexion a réussi, False sinon.
        Raises:
            SerialPortException: en cas d'échec de connexion.
        """
        try:
            self.serial_port = serial.Serial(**params)
            # Correction : ne démarrer le thread de lecture qu'une seule fois !
            self.reader_thread = SerialReaderThread(self.serial_port)
            self.reader_thread.data_received.connect(self._on_data_received)
            self.reader_thread.error_occurred.connect(self._on_reader_error)
            self.reader_thread.connection_lost.connect(self._on_connection_lost)
            self.reader_thread.start()
            return True
        except serial.SerialException as e:
            raise SerialPortException(f"Erreur de connexion série: {e}")
        except Exception as e:
            raise SerialPortException(f"Erreur inattendue: {e}")
            
    def disconnect_port(self) -> None:
        """
        Déconnexion robuste avec nettoyage complet.
        Returns:
            None
        """
        with QMutexLocker(self.mutex):
            if not self.is_connected_flag:
                return
                
            logger.info("Déconnexion en cours...")
            
            try:
                # Arrêter le thread de lecture
                if self.reader_thread:
                    self.reader_thread.stop()
                    if not self.reader_thread.wait(3000):  # Timeout de 3 secondes
                        logger.warning("Timeout lors de l'arrêt du thread de lecture")
                        self.reader_thread.terminate()
                        self.reader_thread.wait(1000)
                    self.reader_thread = None
                    
                # Fermer le port série
                if self.serial_port:
                    try:
                        if self.serial_port.is_open:
                            self.serial_port.close()
                    except Exception as e:
                        logger.warning(f"Erreur lors de la fermeture du port: {e}")
                    finally:
                        self.serial_port = None
                        
                self.is_connected_flag = False
                self.connection_changed.emit(False)
                logger.info("Déconnexion terminée")
                
            except Exception as e:
                logger.error(f"Erreur lors de la déconnexion: {e}")
                self.error_occurred.emit(f"Erreur de déconnexion: {e}")
                
    def is_connected(self) -> bool:
        """
        Vérifie l'état de connexion.
        Returns:
            bool: True si connecté, False sinon.
        """
        with QMutexLocker(self.mutex):
            return (self.is_connected_flag and 
                   self.serial_port is not None and 
                   getattr(self.serial_port, 'is_open', False))
                   
    def send_data(self, data: bytes) -> bool:
        """
        Envoi robuste de données sur le port série.
        Args:
            data (bytes): Données à envoyer (bytes).
        Returns:
            bool: True si l'envoi a réussi, False sinon.
        Raises:
            DataTransmissionException: si les données sont invalides.
        """
        if not isinstance(data, bytes):
            raise DataTransmissionException("Les données doivent être de type bytes")
        if not data:
            logger.warning("Tentative d'envoi de données vides")
            self.error_occurred.emit("Aucune donnée à envoyer (0 octet)")
            return False
        if len(data) > 65536:  # Limite de 64KB
            raise DataTransmissionException("Données trop volumineuses (max 64KB)")
        # DIAGNOSTIC : on désactive temporairement le mutex pour voir si le blocage vient de là
        # with QMutexLocker(self.mutex):
        if not self.is_connected():
            self.error_occurred.emit("Aucune connexion active")
            return False
        try:
            logger.info(f"[DEBUG] Avant serial_port.write, len={len(data)}")
            sent = self.serial_port.write(data) if self.serial_port else 0
            logger.info(f"[DEBUG] Après serial_port.write, sent={sent}")
            if sent is None:
                sent = 0
            self.tx_bytes_count += sent
            if sent == 0:
                logger.warning("Aucun octet réellement envoyé sur le port série !")
                self.error_occurred.emit("Aucun octet envoyé sur le port série !")
                return False
            logger.debug(f"Envoi réussi: {sent} octets")
            return True
        except (serial.SerialException, OSError, IOError) as e:
            error_msg = f"Erreur d'envoi: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
        except Exception as e:
            error_msg = f"Erreur inattendue lors de l'envoi: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
                
    def format_and_send(self, data: str, format_type: str = 'text', eol: str = 'Aucun') -> bool:
        """
        Formate la chaîne selon le type et la fin de ligne, puis envoie sur le port série.
        Args:
            data (str): Données brutes à envoyer.
            format_type (str): 'text' ou 'hex'.
            eol (str): 'Aucun', 'NL', 'CR', 'NL+CR'.
        Returns:
            bool: True si l'envoi a réussi, False sinon.
        """
        # Gestion du format
        if format_type == 'ascii':
            format_type = 'text'
        elif format_type == 'hex':
            format_type = 'hex'
        # Gestion de la fin de ligne
        if eol == 'NL':
            data += '\n'
        elif eol == 'CR':
            data += '\r'
        elif eol == 'NL+CR':
            data += '\r\n'
        elif eol == 'Aucun' or not eol:
            pass  # Ne rien ajouter
        # Conversion selon le format
        if format_type == 'hex':
            try:
                hex_data = data.replace(' ', '').replace('0x', '')
                data_bytes = bytes.fromhex(hex_data)
            except ValueError:
                logger.error("Format hexadécimal invalide")
                self.error_occurred.emit("Format hexadécimal invalide")
                return False
        else:
            data_bytes = data.encode('utf-8')
        return self.send_data(data_bytes)

    def _on_data_received(self, data: bytes) -> None:
        """
        Traite les données reçues du thread de lecture et met à jour les statistiques.
        Args:
            data (bytes): Données reçues (bytes).
        Returns:
            None
        """
        self.rx_bytes_count += len(data)
        self.data_received.emit(data)

    def _on_reader_error(self, error_msg: str) -> None:
        """
        Traite les erreurs du thread de lecture.
        Args:
            error_msg (str): Message d'erreur à propager.
        Returns:
            None
        """
        self.error_occurred.emit(error_msg)

    def _on_connection_lost(self) -> None:
        """
        Traite la perte de connexion série et déclenche la déconnexion.
        Returns:
            None
        """
        logger.warning("Connexion série perdue")
        self.disconnect_port()

    def emit_statistics(self) -> None:
        """
        Émet les statistiques de communication via le signal Qt.
        Returns:
            None
        """
        if self.is_connected():
            uptime = (datetime.now() - self.connection_start_time).total_seconds() if self.connection_start_time else 0
            stats: Dict[str, Any] = {
                'rx_bytes': self.rx_bytes_count,
                'tx_bytes': self.tx_bytes_count,
                'uptime': uptime,
                'connected': True
            }
            self.statistics_updated.emit(stats)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques actuelles de la connexion série.
        Returns:
            Dict[str, Any]: Dictionnaire de statistiques.
        """
        uptime = (datetime.now() - self.connection_start_time).total_seconds() if self.connection_start_time else 0
        return {
            'rx_bytes': self.rx_bytes_count,
            'tx_bytes': self.tx_bytes_count,
            'uptime': uptime,
            'connected': self.is_connected(),
            'error_count': self.error_count
        }

    def reset_statistics(self) -> None:
        """
        Remet à zéro les statistiques de communication.
        Returns:
            None
        """
        with QMutexLocker(self.mutex):
            self.rx_bytes_count = 0
            self.tx_bytes_count = 0
            self.error_count = 0
            if self.is_connected():
                self.connection_start_time = datetime.now()

    def check_connection_health(self) -> None:
        """
        Vérifie la santé de la connexion série.
        Détecte les déconnexions silencieuses et les erreurs persistantes.
        Returns:
            None
        """
        if not self.is_connected():
            return
        try:
            if self.serial_port and hasattr(self.serial_port, 'is_open'):
                if not self.serial_port.is_open:
                    logger.warning("Port série fermé silencieusement")
                    self.disconnect_port()
                    return
            available_ports = [port.device for port in serial.tools.list_ports.comports()]
            if self.serial_port and hasattr(self.serial_port, 'port'):
                current_port = self.serial_port.port
                if current_port not in available_ports:
                    logger.warning(f"Port {current_port} n'est plus disponible - déconnexion détectée")
                    self.error_occurred.emit(f"Port {current_port} déconnecté")
                    self.disconnect_port()
                    return
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de santé: {e}")
            self.disconnect_port()

    def cleanup(self) -> None:
        """
        Nettoyage des ressources lors de la fermeture de l'application.
        Returns:
            None
        """
        try:
            logger.info("Nettoyage du gestionnaire série...")
            if hasattr(self, 'stats_timer') and self.stats_timer:
                self.stats_timer.stop()
            if hasattr(self, 'health_timer') and self.health_timer:
                self.health_timer.stop()
            if self.is_connected():
                self.disconnect_port()
            logger.info("Nettoyage du gestionnaire série terminé")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du gestionnaire série: {e}")

__all__ = []
