#!/usr/bin/env python3
"""
Monitor de Eventos de Windows
Detecta eventos específicos del sistema y envía alertas cuando encuentra códigos sospechosos.
"""

import os
import sys
import time
import json
import logging
import threading
import configparser
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any

try:
    import win32evtlog
    import win32evtlogutil
    import win32con
    import wmi
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError as e:
    print(f"Error: Dependencia faltante - {e}")
    print("Ejecute: pip install pywin32 wmi watchdog")
    sys.exit(1)

from code_analyzer import CodeAnalyzer
from quadient_sender_simple import send_alert

class EventLogMonitor:
    """Monitor para Windows Event Log con detección de eventos críticos del sistema"""
    
    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.running = False
        self.last_check = datetime.now() - timedelta(minutes=5)
        
        # Obtener configuración de eventos
        self.monitored_event_ids = [
            int(x.strip()) for x in 
            config.get('event_monitoring', 'event_ids', fallback='1000,7034,7036,4625,4624').split(',')
        ]
        self.monitored_sources = [
            x.strip() for x in 
            config.get('event_monitoring', 'sources', fallback='System,Application,Security').split(',')
        ]
        
        # Eventos críticos de sistema (reinicio/apagado)
        self.critical_system_events = {
            1074: "Apagado/Reinicio iniciado por usuario o aplicación",
            6005: "Event Log Service iniciado (arranque del sistema)",
            6006: "Event Log Service detenido (apagado del sistema)",
            6008: "Apagado inesperado del sistema",
            1076: "Apagado iniciado pero cancelado",
            6013: "Tiempo de actividad del sistema",
            12: "Inicio del sistema",
            13: "Apagado del sistema",
            41: "Sistema reiniciado sin apagado limpio",
            109: "Kernel Power - Apagado inesperado"
        }
        
        # Event IDs específicos a buscar (si están configurados)
        self.specific_event_search = config.get('event_monitoring', 'specific_event_ids', fallback='').strip()
        if self.specific_event_search:
            self.specific_event_ids = [
                int(x.strip()) for x in self.specific_event_search.split(',') if x.strip()
            ]
        else:
            self.specific_event_ids = []
            
        # Configuración de búsqueda
        self.search_all_events = config.getboolean('event_monitoring', 'search_all_if_not_found', fallback=True)
        
        self.logger.info(f"Monitor configurado para eventos: {self.monitored_event_ids}")
        self.logger.info(f"Eventos críticos de sistema habilitados: {len(self.critical_system_events)}")
        if self.specific_event_ids:
            self.logger.info(f"Búsqueda específica para Event IDs: {self.specific_event_ids}")
        
    def start_monitoring(self):
        """Inicia el monitoreo de Event Log"""
        self.running = True
        self.logger.info("Iniciando monitoreo de Event Log")
        
        while self.running:
            try:
                for source in self.monitored_sources:
                    self._check_event_log(source)
                time.sleep(30)  # Revisar cada 30 segundos
            except Exception as e:
                self.logger.error(f"Error en monitoreo de Event Log: {e}")
                time.sleep(60)
                
    def _check_event_log(self, log_type: str):
        """Revisa un log específico con búsqueda mejorada"""
        try:
            hand = win32evtlog.OpenEventLog('localhost', log_type)
            
            # Leer eventos recientes
            events = win32evtlog.ReadEventLog(
                hand,
                win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ,
                0
            )
            
            events_found = False
            processed_events = 0
            
            for event in events:
                # Limitar búsqueda a eventos recientes
                if event.TimeGenerated < self.last_check:
                    continue
                    
                events_found = True
                processed_events += 1
                
                # Verificar eventos específicos primero (si están configurados)
                if self.specific_event_ids and event.EventID in self.specific_event_ids:
                    self._process_specific_event(event, log_type)
                    continue
                
                # Verificar eventos críticos de sistema (reinicio/apagado)
                if event.EventID in self.critical_system_events:
                    self._process_critical_system_event(event, log_type)
                    continue
                
                # Verificar eventos monitoreados regulares
                if event.EventID in self.monitored_event_ids:
                    self._process_suspicious_event(event, log_type)
                    continue
                
                # Si está habilitado, procesar todos los eventos si no encontramos específicos
                if (self.search_all_events and not self.specific_event_ids and 
                    self._is_potentially_suspicious_event(event)):
                    self._process_general_suspicious_event(event, log_type)
                    
                # Limitar procesamiento para evitar sobrecarga
                if processed_events > 1000:
                    self.logger.warning(f"Límite de eventos alcanzado en {log_type}, deteniendo búsqueda")
                    break
                        
            win32evtlog.CloseEventLog(hand)
            
            if processed_events > 0:
                self.logger.debug(f"Procesados {processed_events} eventos en {log_type}")
            
        except Exception as e:
            self.logger.error(f"Error accediendo a {log_type}: {e}")
            
    def _process_specific_event(self, event, log_type: str):
        """Procesa un evento específico buscado"""
        alert_data = {
            'type': 'specific_event',
            'source': log_type,
            'event_id': event.EventID,
            'source_name': event.SourceName,
            'time': event.TimeGenerated.strftime('%Y-%m-%d %H:%M:%S'),
            'computer': event.ComputerName,
            'severity': 'HIGH'
        }
        
        message = f"🎯 Evento específico encontrado: ID {event.EventID} en {log_type} - {event.SourceName}"
        self.logger.critical(message)
        
        # Enviar alerta inmediata
        threading.Thread(
            target=send_alert,
            args=("EVENTO ESPECÍFICO DETECTADO", message, alert_data)
        ).start()
        
    def _process_critical_system_event(self, event, log_type: str):
        """Procesa eventos críticos del sistema (reinicio/apagado)"""
        event_description = self.critical_system_events.get(event.EventID, "Evento crítico de sistema")
        
        # Determinar severidad basada en el tipo de evento
        severity = 'CRITICAL' if event.EventID in [6008, 41, 109] else 'HIGH'
        
        alert_data = {
            'type': 'system_critical',
            'source': log_type,
            'event_id': event.EventID,
            'source_name': event.SourceName,
            'time': event.TimeGenerated.strftime('%Y-%m-%d %H:%M:%S'),
            'computer': event.ComputerName,
            'severity': severity,
            'description': event_description,
            'category': self._categorize_system_event(event.EventID)
        }
        
        # Obtener información adicional para eventos de reinicio
        additional_info = self._get_shutdown_reboot_details(event)
        if additional_info:
            alert_data.update(additional_info)
        
        message = f"🚨 EVENTO CRÍTICO DE SISTEMA: {event_description} (ID: {event.EventID}) en {event.ComputerName}"
        self.logger.critical(message)
        
        # Enviar alerta crítica inmediata
        threading.Thread(
            target=send_alert,
            args=("🚨 EVENTO CRÍTICO: SISTEMA REINICIO/APAGADO", message, alert_data)
        ).start()
        
    def _process_suspicious_event(self, event, log_type: str):
        """Procesa un evento sospechoso regular"""
        alert_data = {
            'type': 'event_log',
            'source': log_type,
            'event_id': event.EventID,
            'source_name': event.SourceName,
            'time': event.TimeGenerated.strftime('%Y-%m-%d %H:%M:%S'),
            'computer': event.ComputerName,
            'severity': 'HIGH' if event.EventID in [4625, 7034] else 'MEDIUM'
        }
        
        message = f"Evento sospechoso detectado: ID {event.EventID} en {log_type} - {event.SourceName}"
        self.logger.warning(message)
        
        # Enviar alerta
        threading.Thread(
            target=send_alert,
            args=("Evento Sospechoso Detectado", message, alert_data)
        ).start()
        
    def _process_general_suspicious_event(self, event, log_type: str):
        """Procesa eventos potencialmente sospechosos en búsqueda general"""
        alert_data = {
            'type': 'general_suspicious',
            'source': log_type,
            'event_id': event.EventID,
            'source_name': event.SourceName,
            'time': event.TimeGenerated.strftime('%Y-%m-%d %H:%M:%S'),
            'computer': event.ComputerName,
            'severity': 'MEDIUM'
        }
        
        message = f"Evento potencialmente sospechoso: ID {event.EventID} en {log_type} - {event.SourceName}"
        self.logger.info(message)
        
        # Enviar alerta de menor prioridad
        threading.Thread(
            target=send_alert,
            args=("Evento Potencialmente Sospechoso", message, alert_data)
        ).start()
        
    def _is_potentially_suspicious_event(self, event) -> bool:
        """Determina si un evento podría ser sospechoso"""
        # Lista de Event IDs que podrían indicar actividad sospechosa
        suspicious_indicators = [
            # Errores de aplicación
            1000, 1001, 1002,
            # Errores de servicios
            7000, 7001, 7009, 7011, 7023, 7024, 7026, 7031, 7032, 7034,
            # Eventos de seguridad
            4625, 4648, 4720, 4732, 4733, 4756,
            # Eventos de sistema sospechosos
            6005, 6006, 6008, 6009, 6013,
            # Eventos de aplicación sospechosos
            1001, 1002, 1004
        ]
        
        return event.EventID in suspicious_indicators
        
    def _categorize_system_event(self, event_id: int) -> str:
        """Categoriza eventos críticos del sistema"""
        shutdown_events = [1074, 6006, 13, 1076]
        boot_events = [6005, 12]
        crash_events = [6008, 41, 109]
        uptime_events = [6013]
        
        if event_id in shutdown_events:
            return "APAGADO/REINICIO"
        elif event_id in boot_events:
            return "ARRANQUE SISTEMA"
        elif event_id in crash_events:
            return "FALLO CRÍTICO"
        elif event_id in uptime_events:
            return "INFORMACIÓN SISTEMA"
        else:
            return "SISTEMA CRÍTICO"
            
    def _get_shutdown_reboot_details(self, event) -> Dict:
        """Obtiene detalles adicionales para eventos de reinicio/apagado"""
        details = {}
        
        try:
            # Para evento 1074 (shutdown iniciado)
            if event.EventID == 1074:
                # Intentar obtener información del usuario y proceso que inició el shutdown
                if hasattr(event, 'StringInserts') and event.StringInserts:
                    inserts = event.StringInserts
                    if len(inserts) >= 6:
                        details.update({
                            'shutdown_type': inserts[4] if len(inserts) > 4 else 'Unknown',
                            'shutdown_reason': inserts[5] if len(inserts) > 5 else 'Unknown',
                            'initiated_by_user': inserts[1] if len(inserts) > 1 else 'Unknown',
                            'initiated_by_process': inserts[0] if len(inserts) > 0 else 'Unknown'
                        })
                        
            # Para eventos de crash (6008, 41, 109)
            elif event.EventID in [6008, 41, 109]:
                details['crash_type'] = 'UNEXPECTED_SHUTDOWN'
                if event.EventID == 41:
                    details['crash_reason'] = 'Sistema reiniciado sin apagado limpio (Kernel-Power)'
                elif event.EventID == 6008:
                    details['crash_reason'] = 'Apagado inesperado detectado al arrancar'
                elif event.EventID == 109:
                    details['crash_reason'] = 'Kernel detectó que el sistema se reinició sin apagado limpio'
                    
        except Exception as e:
            self.logger.debug(f"Error obteniendo detalles de shutdown/reboot: {e}")
            
        return details

class ProcessMonitor:
    """Monitor de procesos en ejecución"""
    
    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.running = False
        self.wmi_conn = None
        self.code_analyzer = CodeAnalyzer(config, logger)
        
        # Obtener procesos sospechosos de la configuración
        self.suspicious_processes = [
            x.strip().lower() for x in 
            config.get('process_monitoring', 'suspicious_names', 
                      fallback='malware.exe,suspicious.exe,hack.exe').split(',')
        ]
        
        self.suspicious_paths = [
            x.strip().lower() for x in 
            config.get('process_monitoring', 'suspicious_paths', 
                      fallback='temp,downloads,appdata\\local\\temp').split(',')
        ]
        
    def start_monitoring(self):
        """Inicia el monitoreo de procesos"""
        self.running = True
        self.logger.info("Iniciando monitoreo de procesos")
        
        try:
            self.wmi_conn = wmi.WMI()
        except Exception as e:
            self.logger.error(f"Error conectando a WMI: {e}")
            return
            
        while self.running:
            try:
                self._check_running_processes()
                time.sleep(15)  # Revisar cada 15 segundos
            except Exception as e:
                self.logger.error(f"Error en monitoreo de procesos: {e}")
                time.sleep(60)
                
    def _check_running_processes(self):
        """Revisa procesos en ejecución"""
        try:
            for process in self.wmi_conn.Win32_Process():
                if process.Name:
                    process_name = process.Name.lower()
                    
                    # Verificar nombres sospechosos
                    if any(susp in process_name for susp in self.suspicious_processes):
                        self._process_suspicious_process(process, 'suspicious_name')
                        
                    # Verificar rutas sospechosas
                    if process.ExecutablePath:
                        exec_path = process.ExecutablePath.lower()
                        if any(susp_path in exec_path for susp_path in self.suspicious_paths):
                            self._process_suspicious_process(process, 'suspicious_path')
                            
                    # Analizar código si es necesario
                    if process.ExecutablePath and os.path.exists(process.ExecutablePath):
                        if self.code_analyzer.is_suspicious_file(process.ExecutablePath):
                            self._process_suspicious_process(process, 'malicious_code')
                            
        except Exception as e:
            self.logger.error(f"Error revisando procesos: {e}")
            
    def _process_suspicious_process(self, process, reason: str):
        """Procesa un proceso sospechoso"""
        alert_data = {
            'type': 'suspicious_process',
            'process_name': process.Name,
            'process_id': process.ProcessId,
            'executable_path': process.ExecutablePath,
            'command_line': process.CommandLine,
            'reason': reason,
            'severity': 'CRITICAL' if reason == 'malicious_code' else 'HIGH',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        message = f"Proceso sospechoso detectado: {process.Name} (PID: {process.ProcessId}) - Razón: {reason}"
        self.logger.critical(message)
        
        # Enviar alerta inmediata
        threading.Thread(
            target=send_alert,
            args=("PROCESO SOSPECHOSO CRÍTICO", message, alert_data)
        ).start()

class FileSystemMonitor(FileSystemEventHandler):
    """Monitor de cambios en archivos críticos"""
    
    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        super().__init__()
        self.config = config
        self.logger = logger
        self.code_analyzer = CodeAnalyzer(config, logger)
        
        # Obtener extensiones críticas
        self.critical_extensions = [
            x.strip().lower() for x in 
            config.get('file_monitoring', 'critical_extensions', 
                      fallback='.exe,.dll,.sys,.bat,.ps1,.vbs').split(',')
        ]
        
    def on_created(self, event):
        """Archivo creado"""
        if not event.is_directory:
            self._check_file(event.src_path, 'created')
            
    def on_modified(self, event):
        """Archivo modificado"""
        if not event.is_directory:
            self._check_file(event.src_path, 'modified')
            
    def _check_file(self, file_path: str, action: str):
        """Verifica un archivo"""
        try:
            filename = os.path.basename(file_path).lower()
            file_ext = os.path.splitext(filename)[1]
            
            # Solo monitorear extensiones críticas
            if file_ext in self.critical_extensions:
                self.logger.info(f"Archivo {action}: {file_path}")
                
                # Analizar código si es sospechoso
                if self.code_analyzer.is_suspicious_file(file_path):
                    self._process_suspicious_file(file_path, action)
                    
        except Exception as e:
            self.logger.error(f"Error analizando archivo {file_path}: {e}")
            
    def _process_suspicious_file(self, file_path: str, action: str):
        """Procesa un archivo sospechoso"""
        alert_data = {
            'type': 'suspicious_file',
            'file_path': file_path,
            'action': action,
            'severity': 'HIGH',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        message = f"Archivo sospechoso {action}: {file_path}"
        self.logger.warning(message)
        
        # Enviar alerta
        threading.Thread(
            target=send_alert,
            args=("Archivo Sospechoso Detectado", message, alert_data)
        ).start()

class WindowsEventMonitor:
    """Monitor principal que coordina todos los monitores"""
    
    def __init__(self, config_file: str = 'config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # Configurar logging
        self.logger = self._setup_logging()
        
        # Inicializar monitores
        self.event_log_monitor = EventLogMonitor(self.config, self.logger)
        self.process_monitor = ProcessMonitor(self.config, self.logger)
        self.file_monitor = FileSystemMonitor(self.config, self.logger)
        
        # Observer para archivos
        self.file_observer = Observer()
        self._setup_file_monitoring()
        
    def _setup_logging(self) -> logging.Logger:
        """Configura el sistema de logging"""
        logger = logging.getLogger('WindowsEventMonitor')
        logger.setLevel(logging.INFO)
        
        # Crear directorio de logs si no existe
        os.makedirs('logs', exist_ok=True)
        
        # Handler para archivo
        file_handler = logging.FileHandler('logs/windows_events.log')
        file_handler.setLevel(logging.INFO)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    def _setup_file_monitoring(self):
        """Configura el monitoreo de archivos"""
        monitored_paths = [
            x.strip() for x in 
            self.config.get('file_monitoring', 'paths', 
                           fallback='C:\\Windows\\System32,C:\\Users').split(',')
        ]
        
        for path in monitored_paths:
            if os.path.exists(path):
                self.file_observer.schedule(self.file_monitor, path, recursive=True)
                self.logger.info(f"Monitoreando directorio: {path}")
                
    def start(self):
        """Inicia todos los monitores"""
        self.logger.info("Iniciando Windows Event Monitor")
        
        # Iniciar monitoreo de archivos
        self.file_observer.start()
        
        # Iniciar monitores en threads separados
        event_thread = threading.Thread(target=self.event_log_monitor.start_monitoring)
        process_thread = threading.Thread(target=self.process_monitor.start_monitoring)
        
        event_thread.daemon = True
        process_thread.daemon = True
        
        event_thread.start()
        process_thread.start()
        
        try:
            while True:
                time.sleep(60)
                self.logger.info("Windows Event Monitor activo")
        except KeyboardInterrupt:
            self.stop()
            
    def stop(self):
        """Detiene todos los monitores"""
        self.logger.info("Deteniendo Windows Event Monitor")
        
        self.event_log_monitor.running = False
        self.process_monitor.running = False
        self.file_observer.stop()
        self.file_observer.join()

if __name__ == "__main__":
    monitor = WindowsEventMonitor()
    monitor.start()