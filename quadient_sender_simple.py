#!/usr/bin/env python3
"""
Sistema de Alertas Mejorado
Envía notificaciones por múltiples canales: email, webhook, notificaciones Windows.
"""

import os
import json
import time
import smtplib
import requests
import configparser
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

try:
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

class AlertManager:
    """Gestor de alertas que maneja múltiples canales de notificación"""
    
    def __init__(self, config_file: str = 'config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # Configurar logging
        self.logger = self._setup_logging()
        
        # Cache de alertas para evitar spam
        self.alert_cache = {}
        self.cooldown_period = self.config.getint('alerts', 'alert_cooldown', fallback=300)
        
        # Configuración de métodos de alerta
        self.alert_methods = self.config.get('alerts', 'alert_method', fallback='all').lower()
        self.min_severity = self.config.get('alerts', 'min_severity', fallback='MEDIUM').upper()
        
        # Mapeo de severidad a números para comparación
        self.severity_levels = {
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 3,
            'CRITICAL': 4
        }
        
        # Templates de mensajes
        self.message_templates = {
            'event_log': 'Evento crítico detectado en {source}: ID {event_id} - {source_name}',
            'suspicious_process': 'Proceso sospechoso: {process_name} (PID: {process_id}) - {reason}',
            'suspicious_file': 'Archivo sospechoso {action}: {file_path}',
            'system_alert': 'Alerta del sistema: {message}',
            'system_critical': '🚨 EVENTO CRÍTICO DE SISTEMA: {description} en {computer}',
            'specific_event': '🎯 EVENTO ESPECÍFICO DETECTADO: ID {event_id} - {source_name}',
            'general_suspicious': 'Evento potencialmente sospechoso: ID {event_id} - {source_name}'
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Configura el sistema de logging para alertas"""
        logger = logging.getLogger('AlertManager')
        logger.setLevel(logging.INFO)
        
        # Crear directorio de logs si no existe
        os.makedirs('logs', exist_ok=True)
        
        # Handler para archivo
        file_handler = logging.FileHandler('logs/alerts.log')
        file_handler.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
        
    def send_alert(self, title: str, message: str, alert_data: Dict[str, Any] = None) -> bool:
        """Envía una alerta por los canales configurados"""
        try:
            if alert_data is None:
                alert_data = {}
                
            # Verificar severidad mínima
            severity = alert_data.get('severity', 'MEDIUM').upper()
            if self.severity_levels.get(severity, 2) < self.severity_levels.get(self.min_severity, 2):
                self.logger.debug(f"Alerta ignorada por severidad baja: {title}")
                return False
                
            # Verificar cooldown
            if self._is_in_cooldown(title, message):
                self.logger.debug(f"Alerta en cooldown: {title}")
                return False
                
            # Enriquecer datos de alerta
            enriched_data = self._enrich_alert_data(alert_data)
            
            # Generar mensaje formateado
            formatted_message = self._format_message(alert_data.get('type', 'system_alert'), 
                                                   message, enriched_data)
            
            success = True
            
            # Enviar por email
            if self.alert_methods in ['email', 'all']:
                success &= self._send_email_alert(title, formatted_message, enriched_data)
                
            # Enviar por webhook
            if self.alert_methods in ['webhook', 'all']:
                success &= self._send_webhook_alert(title, formatted_message, enriched_data)
                
            # Enviar notificación de Windows
            if self.alert_methods in ['notification', 'all']:
                success &= self._send_notification_alert(title, formatted_message)
                
            # Registrar alerta
            self._log_alert(title, formatted_message, enriched_data, success)
            
            # Actualizar cache
            self._update_cache(title, message)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error enviando alerta: {e}")
            return False
            
    def _enrich_alert_data(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquece los datos de alerta con información adicional"""
        enriched = alert_data.copy()
        enriched.update({
            'timestamp': datetime.now().isoformat(),
            'hostname': os.environ.get('COMPUTERNAME', 'Unknown'),
            'username': os.environ.get('USERNAME', 'Unknown')
        })
        return enriched
        
    def _format_message(self, alert_type: str, message: str, data: Dict[str, Any]) -> str:
        """Formatea el mensaje de alerta usando templates"""
        try:
            if alert_type in self.message_templates:
                template = self.message_templates[alert_type]
                return template.format(**data)
            return message
        except Exception:
            return message
            
    def _send_email_alert(self, title: str, message: str, data: Dict[str, Any]) -> bool:
        """Envía alerta por email"""
        try:
            smtp_server = self.config.get('alerts', 'smtp_server', fallback='')
            smtp_port = self.config.getint('alerts', 'smtp_port', fallback=587)
            username = self.config.get('alerts', 'email_username', fallback='')
            password = self.config.get('alerts', 'email_password', fallback='')
            from_email = self.config.get('alerts', 'email_from', fallback='')
            to_emails = self.config.get('alerts', 'email_to', fallback='').split(',')
            
            if not all([smtp_server, username, password, from_email, to_emails[0]]):
                self.logger.warning("Configuración de email incompleta")
                return False
                
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = f"[ALERTA SEGURIDAD] {title}"
            
            # Cuerpo del mensaje
            body = self._create_email_body(title, message, data)
            msg.attach(MIMEText(body, 'html'))
            
            # Enviar
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
                
            self.logger.info(f"Email enviado: {title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enviando email: {e}")
            return False
            
    def _create_email_body(self, title: str, message: str, data: Dict[str, Any]) -> str:
        """Crea el cuerpo HTML del email"""
        severity_colors = {
            'LOW': '#28a745',
            'MEDIUM': '#ffc107', 
            'HIGH': '#fd7e14',
            'CRITICAL': '#dc3545'
        }
        
        severity = data.get('severity', 'MEDIUM')
        color = severity_colors.get(severity, '#6c757d')
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="border-left: 4px solid {color}; padding-left: 20px;">
                <h2 style="color: {color};">🚨 {title}</h2>
                <p><strong>Severidad:</strong> <span style="color: {color};">{severity}</span></p>
                <p><strong>Mensaje:</strong> {message}</p>
                <p><strong>Hora:</strong> {data.get('timestamp', 'N/A')}</p>
                <p><strong>Equipo:</strong> {data.get('hostname', 'N/A')}</p>
                <p><strong>Usuario:</strong> {data.get('username', 'N/A')}</p>
        """
        
        # Agregar detalles específicos según el tipo
        if data.get('type') == 'system_critical':
            html += f"""
                <h3>🚨 Detalles del Evento Crítico de Sistema:</h3>
                <ul>
                    <li><strong>Categoría:</strong> <span style="color: {color};">{data.get('category', 'N/A')}</span></li>
                    <li><strong>Descripción:</strong> {data.get('description', 'N/A')}</li>
                    <li><strong>Fuente:</strong> {data.get('source', 'N/A')}</li>
                    <li><strong>Event ID:</strong> {data.get('event_id', 'N/A')}</li>
                    <li><strong>Origen:</strong> {data.get('source_name', 'N/A')}</li>
                </ul>
            """
            
            # Agregar detalles específicos de shutdown/reboot si existen
            if data.get('shutdown_type'):
                html += f"""
                    <h4>Información de Apagado/Reinicio:</h4>
                    <ul>
                        <li><strong>Tipo:</strong> {data.get('shutdown_type', 'N/A')}</li>
                        <li><strong>Razón:</strong> {data.get('shutdown_reason', 'N/A')}</li>
                        <li><strong>Iniciado por usuario:</strong> {data.get('initiated_by_user', 'N/A')}</li>
                        <li><strong>Proceso iniciador:</strong> {data.get('initiated_by_process', 'N/A')}</li>
                    </ul>
                """
            elif data.get('crash_reason'):
                html += f"""
                    <h4>⚠️ Información de Fallo del Sistema:</h4>
                    <ul>
                        <li><strong>Tipo de fallo:</strong> {data.get('crash_type', 'N/A')}</li>
                        <li><strong>Razón:</strong> {data.get('crash_reason', 'N/A')}</li>
                    </ul>
                """
                
        elif data.get('type') == 'specific_event':
            html += f"""
                <h3>🎯 Detalles del Evento Específico:</h3>
                <ul>
                    <li><strong>Event ID Buscado:</strong> <span style="color: {color};">{data.get('event_id', 'N/A')}</span></li>
                    <li><strong>Fuente:</strong> {data.get('source', 'N/A')}</li>
                    <li><strong>Origen:</strong> {data.get('source_name', 'N/A')}</li>
                </ul>
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0;">
                    <strong>Nota:</strong> Este evento fue específicamente configurado para monitoreo prioritario.
                </div>
            """
            
        elif data.get('type') == 'suspicious_process':
            html += f"""
                <h3>Detalles del Proceso:</h3>
                <ul>
                    <li><strong>Nombre:</strong> {data.get('process_name', 'N/A')}</li>
                    <li><strong>PID:</strong> {data.get('process_id', 'N/A')}</li>
                    <li><strong>Ruta:</strong> {data.get('executable_path', 'N/A')}</li>
                    <li><strong>Razón:</strong> {data.get('reason', 'N/A')}</li>
                </ul>
            """
        elif data.get('type') == 'event_log':
            html += f"""
                <h3>Detalles del Evento:</h3>
                <ul>
                    <li><strong>Fuente:</strong> {data.get('source', 'N/A')}</li>
                    <li><strong>Event ID:</strong> {data.get('event_id', 'N/A')}</li>
                    <li><strong>Origen:</strong> {data.get('source_name', 'N/A')}</li>
                </ul>
            """
        elif data.get('type') == 'suspicious_file':
            html += f"""
                <h3>Detalles del Archivo:</h3>
                <ul>
                    <li><strong>Ruta:</strong> {data.get('file_path', 'N/A')}</li>
                    <li><strong>Acción:</strong> {data.get('action', 'N/A')}</li>
                </ul>
            """
            
        html += """
            </div>
            <hr>
            <p style="color: #6c757d; font-size: 12px;">
                Este es un mensaje automático del Sistema de Monitoreo de Seguridad.
                No responda a este email.
            </p>
        </body>
        </html>
        """
        
        return html
        
    def _send_webhook_alert(self, title: str, message: str, data: Dict[str, Any]) -> bool:
        """Envía alerta por webhook"""
        try:
            webhook_url = self.config.get('alerts', 'webhook_url', fallback='')
            webhook_method = self.config.get('alerts', 'webhook_method', fallback='POST')
            
            if not webhook_url:
                return False
                
            payload = {
                'title': title,
                'message': message,
                'severity': data.get('severity', 'MEDIUM'),
                'timestamp': data.get('timestamp'),
                'hostname': data.get('hostname'),
                'data': data
            }
            
            # Para Slack, usar formato específico
            if 'slack.com' in webhook_url:
                payload = self._format_slack_message(title, message, data)
                
            response = requests.request(
                webhook_method,
                webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"Webhook enviado: {title}")
                return True
            else:
                self.logger.error(f"Error webhook: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error enviando webhook: {e}")
            return False
            
    def _format_slack_message(self, title: str, message: str, data: Dict[str, Any]) -> Dict:
        """Formatea mensaje para Slack"""
        severity_colors = {
            'LOW': 'good',
            'MEDIUM': 'warning',
            'HIGH': 'danger', 
            'CRITICAL': 'danger'
        }
        
        severity = data.get('severity', 'MEDIUM')
        color = severity_colors.get(severity, 'warning')
        
        return {
            "text": f"🚨 *{title}*",
            "attachments": [{
                "color": color,
                "fields": [
                    {"title": "Mensaje", "value": message, "short": False},
                    {"title": "Severidad", "value": severity, "short": True},
                    {"title": "Equipo", "value": data.get('hostname', 'N/A'), "short": True},
                    {"title": "Hora", "value": data.get('timestamp', 'N/A'), "short": True}
                ]
            }]
        }
        
    def _send_notification_alert(self, title: str, message: str) -> bool:
        """Envía notificación de Windows"""
        try:
            # Intentar con plyer primero
            if PLYER_AVAILABLE:
                timeout = self.config.getint('alerts', 'notification_timeout', fallback=10000)
                notification.notify(
                    title=title,
                    message=message[:200],  # Limitar longitud
                    timeout=timeout // 1000  # plyer usa segundos
                )
                self.logger.info(f"Notificación enviada: {title}")
                return True
                
            # Fallback a win32api si está disponible
            elif WIN32_AVAILABLE:
                win32api.MessageBox(
                    0, 
                    message[:500], 
                    title,
                    win32con.MB_OK | win32con.MB_ICONWARNING | win32con.MB_TOPMOST
                )
                return True
                
            else:
                self.logger.warning("No hay bibliotecas disponibles para notificaciones")
                return False
                
        except Exception as e:
            self.logger.error(f"Error enviando notificación: {e}")
            return False
            
    def _is_in_cooldown(self, title: str, message: str) -> bool:
        """Verifica si la alerta está en período de cooldown"""
        key = f"{title}:{hash(message)}"
        if key in self.alert_cache:
            last_sent = self.alert_cache[key]
            if time.time() - last_sent < self.cooldown_period:
                return True
        return False
        
    def _update_cache(self, title: str, message: str):
        """Actualiza el cache de alertas"""
        key = f"{title}:{hash(message)}"
        self.alert_cache[key] = time.time()
        
        # Limpiar entradas antiguas del cache
        current_time = time.time()
        self.alert_cache = {
            k: v for k, v in self.alert_cache.items()
            if current_time - v < self.cooldown_period * 2
        }
        
    def _log_alert(self, title: str, message: str, data: Dict[str, Any], success: bool):
        """Registra la alerta en el log"""
        log_entry = {
            'title': title,
            'message': message,
            'data': data,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        if success:
            self.logger.info(f"Alerta enviada exitosamente: {title}")
        else:
            self.logger.error(f"Error enviando alerta: {title}")
            
        # Guardar en archivo JSON si está habilitado
        if self.config.getboolean('debugging', 'save_analysis_results', fallback=False):
            alerts_file = os.path.join('logs', 'alerts_history.jsonl')
            with open(alerts_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

# Función legacy para compatibilidad
def send_alert(title: str, message: str, alert_data: Dict[str, Any] = None) -> bool:
    """Función legacy para enviar alertas"""
    alert_manager = AlertManager()
    return alert_manager.send_alert(title, message, alert_data)

if __name__ == "__main__":
    # Ejemplo y prueba
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Prueba del sistema de alertas
        alert_manager = AlertManager()
        
        test_data = {
            'type': 'system_alert',
            'severity': 'HIGH',
            'hostname': 'TEST-PC',
            'message': 'Prueba del sistema de alertas'
        }
        
        success = alert_manager.send_alert(
            "Prueba de Alerta",
            "Este es un mensaje de prueba del sistema de alertas",
            test_data
        )
        
        print(f"Prueba de alerta: {'EXITOSA' if success else 'FALLIDA'}")
    else:
        print("Uso: python quadient_sender_simple.py test")