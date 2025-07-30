#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor Portable Completo de Eventos Windows
Version sin permisos administrativos con funcionalidades avanzadas
Incluye detección de eventos de reinicio/apagado y búsqueda específica
"""

import os
import sys
import time
import json
import logging
import subprocess
import threading
import configparser
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any

# Importaciones opcionales
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

# Importar sistema de alertas
try:
    from quadient_sender_simple import AlertManager, send_alert
    ALERT_SYSTEM_AVAILABLE = True
except ImportError:
    ALERT_SYSTEM_AVAILABLE = False

class PortableWindowsEventMonitor:
    """Monitor portable completo con detección de eventos críticos"""
    
    def __init__(self, config_file: str = 'config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.running = False
        
        # Configurar logging
        self.logger = self._setup_logging()
        
        # Inicializar sistema de alertas
        if ALERT_SYSTEM_AVAILABLE:
            try:
                self.alert_manager = AlertManager(config_file)
            except:
                self.alert_manager = None
                self.logger.warning("Sistema de alertas no disponible")
        else:
            self.alert_manager = None
            
        # Cache de alertas para evitar duplicados
        self.alert_cache = set()
        
        # Configuración de monitoreo
        self.load_monitoring_config()
        
        # Observer para archivos (si está disponible)
        self.file_observer = None
        if WATCHDOG_AVAILABLE:
            self.file_observer = Observer()
            self._setup_file_monitoring()
            
        self.logger.info("Monitor Portable Completo iniciado")
        
    def load_monitoring_config(self):
        """Carga la configuración de monitoreo"""
        # Procesos sospechosos
        self.suspicious_processes = [
            x.strip().lower() for x in 
            self.config.get('process_monitoring', 'suspicious_names', 
                          fallback='malware.exe,virus.exe,trojan.exe,keylogger.exe').split(',')
        ]
        
        # Event IDs específicos (simularemos búsqueda con logs del sistema)
        self.specific_event_ids = []
        specific_ids_str = self.config.get('event_monitoring', 'specific_event_ids', fallback='').strip()
        if specific_ids_str:
            self.specific_event_ids = [int(x.strip()) for x in specific_ids_str.split(',') if x.strip()]
            
        # Intervalos de monitoreo
        self.check_interval = self.config.getint('general', 'check_interval', fallback=30)
        
        # Directorios a monitorear
        paths_str = self.config.get('file_monitoring', 'paths', 
                                  fallback='~/Desktop,~/Downloads,~/Documents')
        self.monitor_paths = []
        for path in paths_str.split(','):
            expanded_path = os.path.expanduser(path.strip())
            if os.path.exists(expanded_path):
                self.monitor_paths.append(expanded_path)
                
        # Extensiones críticas
        self.critical_extensions = [
            x.strip().lower() for x in 
            self.config.get('file_monitoring', 'critical_extensions', 
                          fallback='.exe,.dll,.sys,.bat,.ps1,.vbs').split(',')
        ]
        
    def _setup_logging(self) -> logging.Logger:
        """Configura el sistema de logging"""
        logger = logging.getLogger('PortableMonitor')
        logger.setLevel(logging.INFO)
        
        # Crear directorio de logs
        os.makedirs('logs', exist_ok=True)
        
        # Handler para archivo
        file_handler = logging.FileHandler('logs/portable_monitor.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formato
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    def _setup_file_monitoring(self):
        """Configura el monitoreo de archivos"""
        if not WATCHDOG_AVAILABLE:
            return
            
        file_handler = SuspiciousFileHandler(self)
        
        for path in self.monitor_paths:
            try:
                self.file_observer.schedule(file_handler, path, recursive=True)
                self.logger.info(f"Monitoreando archivos en: {path}")
            except Exception as e:
                self.logger.warning(f"No se puede monitorear {path}: {e}")
                
    def start_monitoring(self):
        """Inicia todos los monitores"""
        self.running = True
        self.logger.info("Iniciando Monitor Portable Completo")
        
        print("🚀 Monitor Portable Completo iniciado")
        print("📊 Funcionalidades:")
        print("  ✅ Monitoreo de procesos sospechosos")
        print("  ✅ Detección de eventos de sistema")
        print("  ✅ Monitoreo de archivos críticos")
        if self.specific_event_ids:
            print(f"  ✅ Búsqueda específica de Event IDs: {self.specific_event_ids}")
        print("  ✅ Sistema de alertas avanzado")
        print("📁 Logs en: logs/portable_monitor.log")
        print("⚠️  Presione Ctrl+C para detener")
        print("=" * 50)
        
        # Iniciar observer de archivos
        if self.file_observer:
            self.file_observer.start()
            
        # Iniciar threads de monitoreo
        threads = []
        
        # Monitor de procesos
        if PSUTIL_AVAILABLE:
            process_thread = threading.Thread(target=self._monitor_processes, daemon=True)
            process_thread.start()
            threads.append(process_thread)
        else:
            # Usar método alternativo sin psutil
            process_thread = threading.Thread(target=self._monitor_processes_alternative, daemon=True)
            process_thread.start()
            threads.append(process_thread)
            
        # Monitor de eventos de sistema
        system_thread = threading.Thread(target=self._monitor_system_events, daemon=True)
        system_thread.start()
        threads.append(system_thread)
        
        # Monitor de reinicio/apagado
        shutdown_thread = threading.Thread(target=self._monitor_shutdown_events, daemon=True)
        shutdown_thread.start()
        threads.append(shutdown_thread)
        
        # Monitor de métricas del sistema
        if PSUTIL_AVAILABLE:
            metrics_thread = threading.Thread(target=self._monitor_system_metrics, daemon=True)
            metrics_thread.start()
            threads.append(metrics_thread)
            
        try:
            while self.running:
                active_threads = sum(1 for t in threads if t.is_alive())
                self.logger.info(f"Monitor activo - Threads: {active_threads}/{len(threads)}")
                time.sleep(60)
        except KeyboardInterrupt:
            self.stop()
            
    def _monitor_processes(self):
        """Monitorea procesos usando psutil"""
        while self.running:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time', 'cmdline']):
                    try:
                        proc_info = proc.info
                        if proc_info['name']:
                            proc_name = proc_info['name'].lower()
                            
                            # Verificar procesos sospechosos
                            if any(susp in proc_name for susp in self.suspicious_processes):
                                self._send_alert(
                                    "Proceso Sospechoso Detectado",
                                    f"Proceso: {proc_info['name']} (PID: {proc_info['pid']})",
                                    {
                                        'type': 'suspicious_process',
                                        'process_name': proc_info['name'],
                                        'process_id': proc_info['pid'],
                                        'executable_path': proc_info.get('exe', 'N/A'),
                                        'severity': 'CRITICAL'
                                    }
                                )
                                
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error monitoreando procesos: {e}")
                time.sleep(60)
                
    def _monitor_processes_alternative(self):
        """Monitorea procesos usando tasklist (método alternativo)"""
        while self.running:
            try:
                # Usar tasklist de Windows
                result = subprocess.run([
                    'tasklist', '/fo', 'csv', '/nh'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            try:
                                parts = [p.strip('"') for p in line.split('","')]
                                if len(parts) >= 2:
                                    proc_name = parts[0].lower()
                                    proc_pid = parts[1]
                                    
                                    # Verificar procesos sospechosos
                                    if any(susp in proc_name for susp in self.suspicious_processes):
                                        self._send_alert(
                                            "Proceso Sospechoso Detectado",
                                            f"Proceso: {parts[0]} (PID: {proc_pid})",
                                            {
                                                'type': 'suspicious_process',
                                                'process_name': parts[0],
                                                'process_id': proc_pid,
                                                'severity': 'CRITICAL'
                                            }
                                        )
                            except:
                                continue
                                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error monitoreando procesos (alternativo): {e}")
                time.sleep(60)
                
    def _monitor_system_events(self):
        """Monitorea eventos del sistema usando métodos alternativos"""
        while self.running:
            try:
                # Buscar eventos específicos si están configurados
                if self.specific_event_ids:
                    self._search_specific_events()
                    
                # Monitorear cambios en el sistema
                self._check_system_changes()
                
                time.sleep(self.check_interval * 2)  # Menos frecuente
                
            except Exception as e:
                self.logger.error(f"Error monitoreando eventos del sistema: {e}")
                time.sleep(120)
                
    def _search_specific_events(self):
        """Busca Event IDs específicos usando wevtutil (si disponible)"""
        try:
            for event_id in self.specific_event_ids:
                # Intentar usar wevtutil para buscar eventos específicos
                try:
                    result = subprocess.run([
                        'wevtutil', 'qe', 'System', 
                        f"/q:*[System[EventID={event_id}]]",
                        '/f:text', '/c:5', '/rd:true'
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        self._send_alert(
                            f"🎯 Evento Específico Encontrado: ID {event_id}",
                            f"Se detectó el Event ID {event_id} que está configurado para monitoreo prioritario",
                            {
                                'type': 'specific_event',
                                'event_id': event_id,
                                'severity': 'HIGH',
                                'source': 'System'
                            }
                        )
                        
                except subprocess.TimeoutExpired:
                    continue
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error buscando eventos específicos: {e}")
            
    def _monitor_shutdown_events(self):
        """Monitorea eventos de reinicio/apagado usando métodos alternativos"""
        last_boot_time = None
        
        while self.running:
            try:
                # Método 1: Verificar tiempo de arranque del sistema
                if PSUTIL_AVAILABLE:
                    current_boot_time = psutil.boot_time()
                    if last_boot_time is not None and current_boot_time != last_boot_time:
                        self._send_alert(
                            "🚨 SISTEMA REINICIADO",
                            f"Se detectó un reinicio del sistema. Nuevo tiempo de arranque: {datetime.fromtimestamp(current_boot_time)}",
                            {
                                'type': 'system_critical',
                                'category': 'REINICIO DETECTADO',
                                'severity': 'CRITICAL',
                                'boot_time': datetime.fromtimestamp(current_boot_time).isoformat()
                            }
                        )
                    last_boot_time = current_boot_time
                    
                # Método 2: Monitorear procesos críticos del sistema
                self._check_critical_system_processes()
                
                time.sleep(60)  # Revisar cada minuto
                
            except Exception as e:
                self.logger.error(f"Error monitoreando eventos de shutdown: {e}")
                time.sleep(120)
                
    def _check_critical_system_processes(self):
        """Verifica procesos críticos que indican estado del sistema"""
        try:
            # Buscar procesos que indican actividad de shutdown
            shutdown_indicators = ['shutdown.exe', 'logoff.exe', 'restart.exe']
            
            if PSUTIL_AVAILABLE:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        proc_info = proc.info
                        if proc_info['name'] and proc_info['name'].lower() in shutdown_indicators:
                            cmdline = ' '.join(proc_info.get('cmdline', []))
                            
                            self._send_alert(
                                "🚨 ACCIÓN DE SISTEMA CRÍTICA DETECTADA",
                                f"Proceso de sistema crítico ejecutándose: {proc_info['name']}",
                                {
                                    'type': 'system_critical',
                                    'category': 'ACCIÓN SISTEMA',
                                    'process_name': proc_info['name'],
                                    'command_line': cmdline,
                                    'severity': 'CRITICAL'
                                }
                            )
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
        except Exception as e:
            self.logger.debug(f"Error verificando procesos críticos: {e}")
            
    def _check_system_changes(self):
        """Verifica cambios en el sistema que puedan indicar eventos importantes"""
        try:
            # Verificar servicios detenidos recientemente
            try:
                result = subprocess.run([
                    'sc', 'query', 'state=', 'stopped'
                ], capture_output=True, text=True, timeout=20)
                
                if result.returncode == 0:
                    # Buscar servicios críticos detenidos
                    critical_services = ['eventlog', 'winmgmt', 'rpcss', 'dcom']
                    output_lower = result.stdout.lower()
                    
                    for service in critical_services:
                        if service in output_lower:
                            self._send_alert(
                                "⚠️ Servicio Crítico Detenido",
                                f"El servicio crítico '{service}' está detenido",
                                {
                                    'type': 'system_alert',
                                    'service_name': service,
                                    'severity': 'HIGH'
                                }
                            )
                            
            except:
                pass
                
        except Exception as e:
            self.logger.debug(f"Error verificando cambios del sistema: {e}")
            
    def _monitor_system_metrics(self):
        """Monitorea métricas del sistema"""
        while self.running:
            try:
                # CPU y memoria
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                cpu_threshold = self.config.getint('system_monitoring', 'cpu_threshold', fallback=90)
                memory_threshold = self.config.getint('system_monitoring', 'memory_threshold', fallback=90)
                
                if cpu_percent > cpu_threshold:
                    self._send_alert(
                        "Alto Uso de CPU",
                        f"CPU al {cpu_percent:.1f}%",
                        {
                            'type': 'system_alert',
                            'metric': 'cpu',
                            'value': cpu_percent,
                            'threshold': cpu_threshold,
                            'severity': 'MEDIUM'
                        }
                    )
                    
                if memory.percent > memory_threshold:
                    self._send_alert(
                        "Alto Uso de Memoria",
                        f"Memoria al {memory.percent:.1f}%",
                        {
                            'type': 'system_alert',
                            'metric': 'memory',
                            'value': memory.percent,
                            'threshold': memory_threshold,
                            'severity': 'MEDIUM'
                        }
                    )
                    
                time.sleep(300)  # Cada 5 minutos
                
            except Exception as e:
                self.logger.error(f"Error monitoreando métricas: {e}")
                time.sleep(300)
                
    def _send_alert(self, title: str, message: str, data: Dict[str, Any]):
        """Envía una alerta usando el sistema disponible"""
        # Evitar alertas duplicadas
        alert_key = f"{title}:{message}"
        if alert_key in self.alert_cache:
            return
        self.alert_cache.add(alert_key)
        
        # Limpiar cache periódicamente
        if len(self.alert_cache) > 100:
            self.alert_cache.clear()
            
        self.logger.warning(f"ALERTA: {title} - {message}")
        
        # Usar sistema de alertas avanzado si está disponible
        if self.alert_manager:
            try:
                threading.Thread(
                    target=self.alert_manager.send_alert,
                    args=(title, message, data),
                    daemon=True
                ).start()
            except Exception as e:
                self.logger.error(f"Error con AlertManager: {e}")
                self._send_basic_alert(title, message)
        else:
            self._send_basic_alert(title, message)
            
    def _send_basic_alert(self, title: str, message: str):
        """Sistema de alertas básico como respaldo"""
        try:
            # Notificación de Windows
            if PLYER_AVAILABLE:
                try:
                    notification.notify(
                        title=title,
                        message=message,
                        timeout=10
                    )
                except:
                    pass
                    
            # Crear archivo de alerta en el escritorio
            try:
                desktop = os.path.expanduser('~/Desktop')
                alert_file = os.path.join(desktop, 'ALERTA_MONITOR.txt')
                with open(alert_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n🚨 ALERTA: {datetime.now()}\n")
                    f.write(f"Título: {title}\n")
                    f.write(f"Mensaje: {message}\n")
                    f.write("-" * 50 + "\n")
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Error enviando alerta básica: {e}")
            
    def stop(self):
        """Detiene el monitoreo"""
        self.running = False
        
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
            
        self.logger.info("Monitor Portable Completo detenido")
        print("\n🛑 Monitor detenido correctamente")

class SuspiciousFileHandler(FileSystemEventHandler):
    """Handler para archivos sospechosos"""
    
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        
    def on_created(self, event):
        if not event.is_directory:
            self._check_file(event.src_path, 'creado')
            
    def on_modified(self, event):
        if not event.is_directory:
            self._check_file(event.src_path, 'modificado')
            
    def _check_file(self, file_path: str, action: str):
        try:
            filename = os.path.basename(file_path).lower()
            file_ext = os.path.splitext(filename)[1]
            
            # Verificar extensiones críticas
            if file_ext in self.monitor.critical_extensions:
                # Verificar patrones sospechosos
                suspicious_patterns = ['malware', 'virus', 'trojan', 'hack', 'crack', 'keygen']
                
                if any(pattern in filename for pattern in suspicious_patterns):
                    self.monitor._send_alert(
                        f"Archivo Sospechoso {action.title()}",
                        f"Archivo: {file_path}",
                        {
                            'type': 'suspicious_file',
                            'file_path': file_path,
                            'action': action,
                            'severity': 'HIGH'
                        }
                    )
                    
        except Exception as e:
            self.monitor.logger.error(f"Error verificando archivo {file_path}: {e}")

if __name__ == "__main__":
    try:
        monitor = PortableWindowsEventMonitor()
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nDeteniendo monitor...")
    except Exception as e:
        print(f"Error: {e}")
        input("Presione Enter para salir...")