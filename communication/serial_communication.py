"""
Gestionnaire série robuste avec QThread et gestion d'erreurs avancée
"""

import time
import serial
import serial.tools.list_ports
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from collections import deque

from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer, QMutex, QMutexLocker
from PyQt5.QtWidgets import QApplication

from system.custom_exceptions import (
    CrazySerialTermException, 
    SerialPortException, 
    ConnectionTimeoutException,
    DataTransmissionException
)
from system.error_handling import retry_with_backoff, CircuitBreaker, ResourceGuard

logger = logging.getLogger("CrazySerialTerm.SerialManager")

class SerialReaderThread(QThread):
    """Thread de lecture série robuste avec gestion d'erreurs avancée."""
    
    data_received = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)
    connection_lost = pyqtSignal()
    
    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.running = False
        self.buffer = deque(maxlen=10000)  # Buffer circulaire limité
        self.read_timeout = 0.1
        self.error_count = 0
        self.max_errors = 5  # Réduit pour une détection plus rapide des déconnexions
        
    def run(self):
        """Boucle principale de lecture."""
        self.running = True
        consecutive_errors = 0
        
        logger.debug("Thread de lecture série démarré")
        
        try:
            while self.running:
                try:
                    if not self.serial_port or not self.serial_port.is_open:
                        logger.warning("Port série fermé, arrêt du thread")
                        break
                        
                    # Lecture non-bloquante avec timeout
                    if self.serial_port.in_waiting > 0:
                        data = self.serial_port.read(min(self.serial_port.in_waiting, 4096))
                        if data:
                            self.data_received.emit(data)
                            consecutive_errors = 0  # Reset en cas de succès
                    else:
                        # Petite pause pour éviter la surcharge CPU
                        self.msleep(10)
                        
                except (serial.SerialException, OSError, IOError, PermissionError) as e:
                    consecutive_errors += 1
                    
                    # Détection spécifique des déconnexions USB
                    if isinstance(e, PermissionError) and e.errno == 22:
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
            
    def stop(self):
        """Arrête le thread proprement."""
        self.running = False
        
class RobustSerialManager(QObject):
    """
    Gestionnaire série robuste avec gestion d'erreurs avancée,
    circuit breaker et retry automatique.
    """
    
    # Signaux thread-safe
    data_received = pyqtSignal(bytes)
    connection_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    statistics_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        
        # État de connexion
        self.serial_port = None
        self.reader_thread = None
        self.is_connected_flag = False
        
        # Thread safety
        self.mutex = QMutex()
        
        # Statistiques
        self.rx_bytes_count = 0
        self.tx_bytes_count = 0
        self.connection_start_time = None
        
        # Robustesse
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30.0)
        self.last_error_time = None
        self.error_count = 0
        
        # Timer pour les statistiques
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.emit_statistics)
        self.stats_timer.start(1000)  # Mise à jour chaque seconde
        
        # Timer de vérification de santé de la connexion
        self.health_timer = QTimer()
        self.health_timer.timeout.connect(self.check_connection_health)
        self.health_timer.start(2000)  # Vérification toutes les 2 secondes
        
    @retry_with_backoff(max_retries=3, exceptions=(serial.SerialException, OSError))
    def get_available_ports(self) -> List[str]:
        """Liste les ports série disponibles avec retry automatique."""
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            logger.debug(f"Ports trouvés: {ports}")
            return ports
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des ports: {e}")
            raise SerialConnectionError(f"Impossible de lister les ports: {e}")
            
    def get_port_info(self, port_name: str) -> Dict[str, Any]:
        """Obtient les informations détaillées d'un port."""
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
            
    def connect(self, port: str, **kwargs) -> bool:
        """
        Connexion robuste avec validation et gestion d'erreurs.
        """
        with QMutexLocker(self.mutex):
            if self.is_connected_flag:
                self.disconnect_port()
                
            try:
                # Validation des paramètres
                if not port or not isinstance(port, str):
                    raise SerialConnectionError("Port invalide")
                    
                # Paramètres par défaut sécurisés
                params = {
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
                
                # Validation des paramètres
                self._validate_serial_params(params)
                
                # Utilisation du circuit breaker
                def _connect():
                    return self._do_connect(params)
                    
                result = self.circuit_breaker.call(_connect)
                
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
                
    def _validate_serial_params(self, params: Dict[str, Any]):
        """Valide les paramètres de connexion série."""
        valid_baudrates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        valid_bytesizes = [5, 6, 7, 8]
        valid_parities = ['N', 'E', 'O', 'M', 'S']
        valid_stopbits = [1, 1.5, 2]
        
        if params['baudrate'] not in valid_baudrates:
            raise SerialConnectionError(f"Baudrate invalide: {params['baudrate']}")
        if params['bytesize'] not in valid_bytesizes:
            raise SerialConnectionError(f"Bytesize invalide: {params['bytesize']}")
        if params['parity'] not in valid_parities:
            raise SerialConnectionError(f"Parité invalide: {params['parity']}")
        if params['stopbits'] not in valid_stopbits:
            raise SerialConnectionError(f"Stop bits invalides: {params['stopbits']}")
            
    def _do_connect(self, params: Dict[str, Any]) -> bool:
        """Effectue la connexion série réelle."""
        try:
            self.serial_port = serial.Serial(**params)
            
            # Démarrer le thread de lecture
            self.reader_thread = SerialReaderThread(self.serial_port)
            self.reader_thread.data_received.connect(self._on_data_received)
            self.reader_thread.error_occurred.connect(self._on_reader_error)
            self.reader_thread.connection_lost.connect(self._on_connection_lost)
            self.reader_thread.start()
            
            return True
            
        except serial.SerialException as e:
            raise SerialConnectionError(f"Erreur de connexion série: {e}")
        except Exception as e:
            raise SerialConnectionError(f"Erreur inattendue: {e}")
            
    def disconnect_port(self):
        """Déconnexion robuste avec nettoyage complet."""
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
        """Vérifie l'état de connexion."""
        with QMutexLocker(self.mutex):
            return (self.is_connected_flag and 
                   self.serial_port and 
                   self.serial_port.is_open)
                   
    def send_data(self, data: bytes) -> bool:
        """Envoi robuste de données."""
        if not isinstance(data, bytes):
            raise SerialDataError("Les données doivent être de type bytes")
            
        if not data:
            logger.warning("Tentative d'envoi de données vides")
            return False
            
        if len(data) > 65536:  # Limite de 64KB
            raise SerialDataError("Données trop volumineuses (max 64KB)")
            
        with QMutexLocker(self.mutex):
            if not self.is_connected():
                self.error_occurred.emit("Aucune connexion active")
                return False
                
            try:
                # Envoi par chunks pour éviter les blocages
                chunk_size = 1024
                total_sent = 0
                
                for i in range(0, len(data), chunk_size):
                    chunk = data[i:i + chunk_size]
                    sent = self.serial_port.write(chunk)
                    total_sent += sent
                    
                    # Forcer l'envoi
                    self.serial_port.flush()
                    
                self.tx_bytes_count += total_sent
                logger.debug(f"Envoi réussi: {total_sent} octets")
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
                
    def _on_data_received(self, data: bytes):
        """Traite les données reçues du thread de lecture."""
        self.rx_bytes_count += len(data)
        self.data_received.emit(data)
        
    def _on_reader_error(self, error_msg: str):
        """Traite les erreurs du thread de lecture."""
        self.error_occurred.emit(error_msg)
        
    def _on_connection_lost(self):
        """Traite la perte de connexion."""
        logger.warning("Connexion série perdue")
        self.disconnect_port()
        
    def emit_statistics(self):
        """Émet les statistiques de communication."""
        if self.is_connected():
            uptime = (datetime.now() - self.connection_start_time).total_seconds() if self.connection_start_time else 0
            stats = {
                'rx_bytes': self.rx_bytes_count,
                'tx_bytes': self.tx_bytes_count,
                'uptime': uptime,
                'connected': True
            }
            self.statistics_updated.emit(stats)
            
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques actuelles."""
        uptime = (datetime.now() - self.connection_start_time).total_seconds() if self.connection_start_time else 0
        return {
            'rx_bytes': self.rx_bytes_count,
            'tx_bytes': self.tx_bytes_count,
            'uptime': uptime,
            'connected': self.is_connected(),
            'error_count': self.error_count
        }
        
    def reset_statistics(self):
        """Remet à zéro les statistiques."""
        with QMutexLocker(self.mutex):
            self.rx_bytes_count = 0
            self.tx_bytes_count = 0
            self.error_count = 0
            if self.is_connected():
                self.connection_start_time = datetime.now()
                
    def check_connection_health(self):
        """
        Vérifie la santé de la connexion série.
        Détecte les déconnexions silencieuses et les erreurs persistantes.
        """
        if not self.is_connected():
            return
            
        try:
            # Vérifier si le port série est toujours accessible
            if self.serial_port and hasattr(self.serial_port, 'is_open'):
                if not self.serial_port.is_open:
                    logger.warning("Port série fermé silencieusement")
                    self.disconnect_port()
                    return
                    
            # Vérifier si le périphérique est toujours présent dans la liste des ports
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
            # En cas d'erreur lors de la vérification, forcer la déconnexion
            self.disconnect_port()
            
    def cleanup(self):
        """Nettoyage des ressources lors de la fermeture de l'application."""
        try:
            logger.info("Nettoyage du gestionnaire série...")
            
            # Arrêter tous les timers
            if hasattr(self, 'stats_timer') and self.stats_timer:
                self.stats_timer.stop()
                
            if hasattr(self, 'health_timer') and self.health_timer:
                self.health_timer.stop()
                
            # Déconnecter si connecté
            if self.is_connected():
                self.disconnect_port()
                
            logger.info("Nettoyage du gestionnaire série terminé")
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du gestionnaire série: {e}")
