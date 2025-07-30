#!/usr/bin/env python3
"""
Monitor Ultra Portable de Eventos Windows
Version minimalista que funciona SIN permisos administrativos
Solo requiere Python básico - NO necesita instalaciones adicionales
"""

import os
import sys
import time
import json
import subprocess
import threading
import urllib.request
import urllib.parse
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from typing import Dict, List, Optional

class UltraPortableMonitor:
    """Monitor ultra portable que funciona solo con Python estándar"""
    
    def __init__(self):
        self.running = False
        self.alerts_sent = set()
        
        # Configuración básica (modificable)
        self.config = {
            'check_interval': 30,
            'suspicious_processes': [
                'malware.exe', 'virus.exe', 'trojan.exe', 'keylogger.exe',
                'hack.exe', 'crack.exe', 'suspicious.exe', 'backdoor.exe'
            ],
            'suspicious_files': [
                'malware', 'virus', 'trojan', 'hack', 'crack', 'keygen'
            ],
            'monitor_dirs': [
                os.path.expanduser('~/Desktop'),
                os.path.expanduser('~/Downloads'),
                os.path.expanduser('~/Documents'),
                os.path.expanduser('~/AppData/Local/Temp')
            ],
            'email_alerts': False,  # Cambiar a True para activar email
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email_user': '',  # Configurar email
            'email_pass': '',  # Configurar password
            'email_to': '',    # Email destino
            'webhook_url': '', # URL de webhook (Slack, Discord, etc.)
        }
        
        # Logs en directorio del usuario si no hay permisos
        try:
            self.log_dir = 'logs'
            os.makedirs(self.log_dir, exist_ok=True)
        except:
            self.log_dir = os.path.expanduser('~/.monitor_logs')
            os.makedirs(self.log_dir, exist_ok=True)
            
        self.log_file = os.path.join(self.log_dir, 'ultra_portable_monitor.log')
        
        self._log("Monitor Ultra Portable iniciado")
        
    def _log(self, message: str, level: str = "INFO"):
        """Log simple a archivo y consola"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}"
        
        # Consola
        print(log_entry)
        
        # Archivo
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except:
            pass  # Silencioso si no puede escribir
            
    def _send_alert(self, title: str, message: str, severity: str = "HIGH"):
        """Envía alertas por múltiples canales"""
        alert_key = f"{title}:{message}"
        
        # Evitar spam de alertas repetidas
        if alert_key in self.alerts_sent:
            return
            
        self.alerts_sent.add(alert_key)
        
        self._log(f"ALERTA {severity}: {title} - {message}", "ALERT")
        
        # Notificación de Windows (sin dependencias externas)
        self._show_windows_notification(title, message)
        
        # Email si está configurado
        if self.config['email_alerts'] and self.config['email_user']:
            threading.Thread(target=self._send_email, args=(title, message)).start()
            
        # Webhook si está configurado
        if self.config['webhook_url']:
            threading.Thread(target=self._send_webhook, args=(title, message, severity)).start()
            
    def _show_windows_notification(self, title: str, message: str):
        """Muestra notificación de Windows usando solo librerías estándar"""
        try:
            # Método 1: msg command (disponible en Windows)
            subprocess.run([
                'msg', os.environ.get('USERNAME', '*'), 
                f"{title}\n\n{message}"
            ], capture_output=True, timeout=5)
        except:
            try:
                # Método 2: PowerShell Toast (Windows 10+)
                ps_script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                $notify = New-Object System.Windows.Forms.NotifyIcon
                $notify.Icon = [System.Drawing.SystemIcons]::Warning
                $notify.BalloonTipTitle = "{title}"
                $notify.BalloonTipText = "{message}"
                $notify.Visible = $true
                $notify.ShowBalloonTip(10000)
                Start-Sleep -Seconds 3
                $notify.Dispose()
                '''
                subprocess.run(['powershell', '-Command', ps_script], 
                             capture_output=True, timeout=10)
            except:
                # Método 3: Escribir a archivo visible
                try:
                    alert_file = os.path.join(os.path.expanduser('~/Desktop'), 
                                            'ALERTA_SEGURIDAD.txt')
                    with open(alert_file, 'w', encoding='utf-8') as f:
                        f.write(f"🚨 ALERTA DE SEGURIDAD 🚨\n\n")
                        f.write(f"Título: {title}\n")
                        f.write(f"Mensaje: {message}\n")
                        f.write(f"Hora: {datetime.now()}\n\n")
                        f.write("Este archivo se generó automáticamente por el Monitor de Seguridad.\n")
                except:
                    pass
                    
    def _send_email(self, title: str, message: str):
        """Envía email usando solo librerías estándar"""
        try:
            msg = MIMEText(f"""
🚨 ALERTA DE SEGURIDAD 🚨

Título: {title}
Mensaje: {message}
Hora: {datetime.now()}
Equipo: {os.environ.get('COMPUTERNAME', 'Desconocido')}
Usuario: {os.environ.get('USERNAME', 'Desconocido')}

Este es un mensaje automático del Monitor Ultra Portable.
            """)
            
            msg['Subject'] = f"[ALERTA SEGURIDAD] {title}"
            msg['From'] = self.config['email_user']
            msg['To'] = self.config['email_to']
            
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['email_user'], self.config['email_pass'])
                server.send_message(msg)
                
            self._log("Email enviado correctamente")
            
        except Exception as e:
            self._log(f"Error enviando email: {e}", "ERROR")
            
    def _send_webhook(self, title: str, message: str, severity: str):
        """Envía webhook usando solo librerías estándar"""
        try:
            data = {
                'text': f"🚨 **{title}**",
                'attachments': [{
                    'color': 'danger' if severity == 'CRITICAL' else 'warning',
                    'fields': [
                        {'title': 'Mensaje', 'value': message, 'short': False},
                        {'title': 'Severidad', 'value': severity, 'short': True},
                        {'title': 'Equipo', 'value': os.environ.get('COMPUTERNAME', 'N/A'), 'short': True},
                        {'title': 'Hora', 'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'short': True}
                    ]
                }]
            }
            
            json_data = json.dumps(data).encode('utf-8')
            
            req = urllib.request.Request(
                self.config['webhook_url'],
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    self._log("Webhook enviado correctamente")
                else:
                    self._log(f"Error webhook: status {response.status}", "ERROR")
                    
        except Exception as e:
            self._log(f"Error enviando webhook: {e}", "ERROR")
            
    def _get_running_processes(self) -> List[Dict]:
        """Obtiene procesos en ejecución usando solo Windows estándar"""
        processes = []
        
        try:
            # Usar tasklist (disponible en Windows)
            result = subprocess.run([
                'tasklist', '/fo', 'csv', '/nh'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            # Parse CSV simple
                            parts = [p.strip('"') for p in line.split('","')]
                            if len(parts) >= 2:
                                processes.append({
                                    'name': parts[0],
                                    'pid': parts[1],
                                    'memory': parts[4] if len(parts) > 4 else 'N/A'
                                })
                        except:
                            continue
                            
        except Exception as e:
            self._log(f"Error obteniendo procesos: {e}", "ERROR")
            
        return processes
        
    def _monitor_processes(self):
        """Monitorea procesos sospechosos"""
        while self.running:
            try:
                processes = self._get_running_processes()
                
                for proc in processes:
                    proc_name = proc['name'].lower()
                    
                    # Verificar nombres sospechosos
                    for suspicious in self.config['suspicious_processes']:
                        if suspicious.lower() in proc_name:
                            self._send_alert(
                                "Proceso Sospechoso Detectado",
                                f"Proceso: {proc['name']} (PID: {proc['pid']})",
                                "CRITICAL"
                            )
                            break
                            
                # Verificar uso excesivo de CPU/Memoria usando wmic
                try:
                    cpu_result = subprocess.run([
                        'wmic', 'cpu', 'get', 'loadpercentage', '/value'
                    ], capture_output=True, text=True, timeout=10)
                    
                    for line in cpu_result.stdout.split('\n'):
                        if 'LoadPercentage=' in line:
                            cpu_usage = int(line.split('=')[1].strip())
                            if cpu_usage > 95:
                                self._send_alert(
                                    "Alto Uso de CPU",
                                    f"CPU al {cpu_usage}%",
                                    "HIGH"
                                )
                            break
                except:
                    pass
                    
                time.sleep(self.config['check_interval'])
                
            except Exception as e:
                self._log(f"Error monitoreando procesos: {e}", "ERROR")
                time.sleep(60)
                
    def _monitor_files(self):
        """Monitorea archivos sospechosos en directorios del usuario"""
        known_files = set()
        
        # Obtener archivos iniciales
        for directory in self.config['monitor_dirs']:
            if os.path.exists(directory):
                try:
                    for root, dirs, files in os.walk(directory):
                        for file in files:
                            file_path = os.path.join(root, file)
                            known_files.add(file_path)
                except:
                    continue
                    
        while self.running:
            try:
                current_files = set()
                
                for directory in self.config['monitor_dirs']:
                    if os.path.exists(directory):
                        try:
                            for root, dirs, files in os.walk(directory):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    current_files.add(file_path)
                                    
                                    # Archivo nuevo
                                    if file_path not in known_files:
                                        self._check_suspicious_file(file_path)
                        except:
                            continue
                            
                known_files = current_files
                time.sleep(self.config['check_interval'] * 2)  # Menos frecuente
                
            except Exception as e:
                self._log(f"Error monitoreando archivos: {e}", "ERROR")
                time.sleep(120)
                
    def _check_suspicious_file(self, file_path: str):
        """Verifica si un archivo es sospechoso"""
        try:
            filename = os.path.basename(file_path).lower()
            
            # Verificar nombre sospechoso
            for suspicious in self.config['suspicious_files']:
                if suspicious in filename:
                    self._send_alert(
                        "Archivo Sospechoso Detectado",
                        f"Archivo: {file_path}",
                        "HIGH"
                    )
                    return
                    
            # Verificar extensiones peligrosas
            dangerous_extensions = ['.exe', '.scr', '.bat', '.cmd', '.ps1', '.vbs', '.js']
            _, ext = os.path.splitext(filename)
            
            if ext in dangerous_extensions:
                # Solo alertar si tiene nombre sospechoso también
                suspicious_keywords = ['temp', 'new', 'untitled', 'download']
                if any(keyword in filename for keyword in suspicious_keywords):
                    self._send_alert(
                        "Archivo Ejecutable Sospechoso",
                        f"Archivo: {file_path}",
                        "MEDIUM"
                    )
                    
        except Exception as e:
            self._log(f"Error verificando archivo {file_path}: {e}", "ERROR")
            
    def _monitor_network(self):
        """Monitorea conexiones de red sospechosas"""
        while self.running:
            try:
                # Usar netstat para ver conexiones
                result = subprocess.run([
                    'netstat', '-an'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    suspicious_ports = [4444, 5555, 6666, 7777, 8888, 31337, 12345]
                    
                    for line in lines:
                        if 'ESTABLISHED' in line or 'LISTENING' in line:
                            for port in suspicious_ports:
                                if f":{port}" in line:
                                    self._send_alert(
                                        "Puerto Sospechoso Detectado",
                                        f"Conexión en puerto {port}: {line.strip()}",
                                        "HIGH"
                                    )
                                    
                time.sleep(self.config['check_interval'] * 4)  # Menos frecuente
                
            except Exception as e:
                self._log(f"Error monitoreando red: {e}", "ERROR")
                time.sleep(240)
                
    def start_monitoring(self):
        """Inicia el monitoreo"""
        self.running = True
        self._log("Iniciando monitoreo ultra portable...")
        
        print("🚀 Monitor Ultra Portable iniciado")
        print("📁 Logs en:", self.log_file)
        print("⚠️  Presione Ctrl+C para detener")
        print("=" * 50)
        
        # Iniciar threads de monitoreo
        threads = [
            threading.Thread(target=self._monitor_processes, daemon=True),
            threading.Thread(target=self._monitor_files, daemon=True),
            threading.Thread(target=self._monitor_network, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
            
        try:
            while self.running:
                time.sleep(60)
                active_threads = sum(1 for t in threads if t.is_alive())
                self._log(f"Monitor activo - Threads: {active_threads}/3")
                
        except KeyboardInterrupt:
            self.stop()
            
    def stop(self):
        """Detiene el monitoreo"""
        self.running = False
        self._log("Monitor ultra portable detenido")
        print("\n🛑 Monitor detenido")
        
    def configure_email(self, smtp_server: str, email_user: str, email_pass: str, email_to: str):
        """Configura alertas por email"""
        self.config.update({
            'email_alerts': True,
            'smtp_server': smtp_server,
            'email_user': email_user,
            'email_pass': email_pass,
            'email_to': email_to
        })
        self._log("Configuración de email actualizada")
        
    def configure_webhook(self, webhook_url: str):
        """Configura webhook (Slack, Discord, etc.)"""
        self.config['webhook_url'] = webhook_url
        self._log("Webhook configurado")

def main():
    """Función principal"""
    print("🔐 Monitor Ultra Portable de Eventos Windows")
    print("📱 Versión sin permisos administrativos")
    print("🚀 Solo requiere Python estándar")
    print("=" * 50)
    
    monitor = UltraPortableMonitor()
    
    # Configuración interactiva opcional
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        print("\n⚙️  CONFIGURACIÓN OPCIONAL:")
        
        email = input("Email para alertas (Enter para omitir): ").strip()
        if email:
            password = input("Password del email: ").strip()
            email_to = input("Email destino: ").strip()
            if password and email_to:
                monitor.configure_email('smtp.gmail.com', email, password, email_to)
                print("✅ Email configurado")
                
        webhook = input("URL de webhook (Slack/Discord, Enter para omitir): ").strip()
        if webhook:
            monitor.configure_webhook(webhook)
            print("✅ Webhook configurado")
            
    # Iniciar monitoreo
    try:
        monitor.start_monitoring()
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Presione Enter para salir...")

if __name__ == "__main__":
    main()