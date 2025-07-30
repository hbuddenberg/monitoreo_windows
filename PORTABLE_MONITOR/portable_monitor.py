# -*- coding: utf-8 -*-
# Monitor de Eventos Windows - Version Portable Sin Permisos Admin
# Funciona con capacidades limitadas pero sin requerir permisos administrativos

import os
import sys
import time
import json
import logging
import psutil
import requests
import threading
import configparser
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Intentar importar dependencias opcionales
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

class PortableEventMonitor:
    """Monitor portable que funciona sin permisos administrativos"""
    def __init__(self, config_file: str = 'config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.running = False
        # Configurar logging
        self.logger = self._setup_logging()
        # Obtener directorio del usuario para logs
        self.user_temp = os.path.expanduser('~')
        self.log_dir = os.path.join(self.user_temp, '.monitor_eventos')
        os.makedirs(self.log_dir, exist_ok=True)
        self.logger.info("Monitor portable iniciado sin permisos administrativos")
    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger('PortableMonitor')
        logger.setLevel(logging.INFO)
        # Crear handler para archivo en directorio del usuario
        try:
            log_file = os.path.join('logs', 'portable_monitor.log')
            os.makedirs('logs', exist_ok=True)
            file_handler = logging.FileHandler(log_file)
        except:
            # Si no puede escribir en logs, usar temp del usuario
            user_temp = os.path.expanduser('~')
            log_file = os.path.join(user_temp, 'monitor_eventos.log')
            file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger
    def start_monitoring(self):
        """Inicia el monitoreo con capacidades limitadas"""
        self.running = True
        self.logger.info("Iniciando monitoreo portable...")
        # Threads para diferentes tipos de monitoreo
        threads = []
        # Monitor de procesos (usando psutil)
        process_thread = threading.Thread(target=self._monitor_processes)
        process_thread.daemon = True
        process_thread.start()
        threads.append(process_thread)
        # Monitor de archivos (si watchdog esta disponible)
        if WATCHDOG_AVAILABLE:
            file_thread = threading.Thread(target=self._monitor_files)
            file_thread.daemon = True
            file_thread.start()
            threads.append(file_thread)
        # Monitor de sistema
        system_thread = threading.Thread(target=self._monitor_system)
        system_thread.daemon = True
        system_thread.start()
        threads.append(system_thread)
        try:
            while self.running:
                time.sleep(60)
                self.logger.info(f"Monitor portable activo - Threads: {len(threads)}")
        except KeyboardInterrupt:
            self.stop()
    def _monitor_processes(self):
        """Monitorea procesos usando psutil"""
        suspicious_names = ['malware.exe', 'suspicious.exe', 'hack.exe', 'keylogger.exe']
        while self.running:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
                    try:
                        proc_info = proc.info
                        if proc_info['name']:
                            proc_name = proc_info['name'].lower()
                            # Verificar nombres sospechosos
                            if any(susp in proc_name for susp in suspicious_names):
                                self._send_alert(
                                    "Proceso Sospechoso Detectado",
                                    f"Proceso: {proc_info['name']} (PID: {proc_info['pid']}^)",
                                    {'type': 'suspicious_process', 'severity': 'HIGH'}
                                )
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                time.sleep(30)  # Revisar cada 30 segundos
            except Exception as e:
                self.logger.error(f"Error monitoreando procesos: {e}")
                time.sleep(60)
    def _monitor_files(self):
        """Monitorea archivos usando watchdog"""
        if not WATCHDOG_AVAILABLE:
            return
        # Solo monitorear directorios accesibles sin permisos admin
        user_dirs = [
            os.path.expanduser('~/Desktop'),
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~/Documents')
        ]
        class FileHandler(FileSystemEventHandler):
            def __init__(self, monitor):
                self.monitor = monitor
            def on_created(self, event):
                if not event.is_directory:
                    self.monitor._check_suspicious_file(event.src_path)
        observer = Observer()
        handler = FileHandler(self)
        for user_dir in user_dirs:
            if os.path.exists(user_dir):
                try:
                    observer.schedule(handler, user_dir, recursive=True)
                    self.logger.info(f"Monitoreando: {user_dir}")
                except Exception as e:
                    self.logger.warning(f"No se puede monitorear {user_dir}: {e}")
        observer.start()
        try:
            while self.running:
                time.sleep(60)
        except:
            pass
        finally:
            observer.stop()
            observer.join()
    def _monitor_system(self):
        """Monitorea métricas del sistema"""
        while self.running:
            try:
                # Monitorear CPU y memoria
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                # Alertar si uso excesivo
                if cpu_percent > 90:
                    self._send_alert(
                        "Alto Uso de CPU",
                        f"CPU al {cpu_percent}%",
                        {'type': 'system_alert', 'severity': 'MEDIUM'}
                    )
                if memory.percent > 90:
                    self._send_alert(
                        "Alto Uso de Memoria",
                        f"Memoria al {memory.percent}%",
                        {'type': 'system_alert', 'severity': 'MEDIUM'}
                    )
                time.sleep(300)  # Revisar cada 5 minutos
            except Exception as e:
                self.logger.error(f"Error monitoreando sistema: {e}")
                time.sleep(300)
    def _check_suspicious_file(self, file_path: str):
        """Verifica si un archivo es sospechoso"""
        try:
            filename = os.path.basename(file_path).lower()
            suspicious_extensions = ['.exe', '.scr', '.bat', '.cmd', '.ps1']
            suspicious_names = ['malware', 'virus', 'trojan', 'hack', 'crack']
            # Verificar extensión
            _, ext = os.path.splitext(filename)
            if ext in suspicious_extensions:
                # Verificar nombre sospechoso
                if any(name in filename for name in suspicious_names):
                    self._send_alert(
                        "Archivo Sospechoso Detectado",
                        f"Archivo: {file_path}",
                        {'type': 'suspicious_file', 'severity': 'HIGH'}
                    )
        except Exception as e:
            self.logger.error(f"Error verificando archivo {file_path}: {e}")
    def _send_alert(self, title: str, message: str, data: Dict):
        """Envía una alerta"""
        try:
            self.logger.warning(f"ALERTA: {title} - {message}")
            # Notificación de Windows si está disponible
            if PLYER_AVAILABLE:
                try:
                    notification.notify(
                        title=title,
                        message=message,
                        timeout=10
                    )
                except:
                    pass
            # Intentar enviar por email (si está configurado)
            try:
                from quadient_sender_simple import send_alert
                threading.Thread(
                    target=send_alert,
                    args=(title, message, data)
                ).start()
            except Exception as e:
                self.logger.debug(f"No se pudo enviar email: {e}")
        except Exception as e:
            self.logger.error(f"Error enviando alerta: {e}")
    def stop(self):
        """Detiene el monitoreo"""
        self.running = False
        self.logger.info("Monitor portable detenido")
if __name__ == "__main__":
    try:
        monitor = PortableEventMonitor()
        print("Iniciando Monitor Portable de Eventos...")
        print("Presione Ctrl+C para detener")
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\\nDeteniendo monitor...")
    except Exception as e:
        print(f"Error: {e}")
        input("Presione Enter para salir...")
