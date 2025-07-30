#!/usr/bin/env python3
"""
Sistema de Alertas Multi-Plataforma Completo
Envía notificaciones de seguridad a 9 plataformas diferentes:
- Slack (webhooks con attachments)
- Telegram (Bot API con HTML formatting)
- Discord (webhooks con embeds ricos)
- Microsoft Teams (Adaptive Cards)
- WhatsApp Business API (mensajes y templates)
- Pushover (notificaciones móviles con prioridades)
- Email (HTML con formato rico)
- Webhooks genéricos (JSON personalizable)
- Notificaciones Windows (toast/messagebox)

Características:
- Formateo inteligente por plataforma
- Rate limiting y cooldown anti-spam
- Múltiples destinatarios por plataforma
- Severidades configurables (LOW, MEDIUM, HIGH, CRITICAL)
- Logging completo y manejo de errores
- Sistema de pruebas integrado

Uso:
    python quadient_sender_simple.py test          # Probar todas las plataformas
    python quadient_sender_simple.py slack         # Probar solo Slack
    python quadient_sender_simple.py help          # Ver ayuda completa

Configuración:
    Editar config.ini para habilitar y configurar cada plataforma
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
                
            # Enviar por webhook genérico
            if self.alert_methods in ['webhook', 'all']:
                success &= self._send_webhook_alert(title, formatted_message, enriched_data)
                
            # Enviar por Telegram
            if self.alert_methods in ['telegram', 'all']:
                success &= self._send_telegram_alert(title, formatted_message, enriched_data)
                
            # Enviar por Discord
            if self.alert_methods in ['discord', 'all']:
                success &= self._send_discord_alert(title, formatted_message, enriched_data)
                
            # Enviar por Slack
            if self.alert_methods in ['slack', 'all']:
                success &= self._send_slack_alert(title, formatted_message, enriched_data)
                
            # Enviar por WhatsApp
            if self.alert_methods in ['whatsapp', 'all']:
                success &= self._send_whatsapp_alert(title, formatted_message, enriched_data)
                
            # Enviar por Microsoft Teams
            if self.alert_methods in ['teams', 'all']:
                success &= self._send_teams_alert(title, formatted_message, enriched_data)
                
            # Enviar por Pushover
            if self.alert_methods in ['pushover', 'all']:
                success &= self._send_pushover_alert(title, formatted_message, enriched_data)
                
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
            
    def _send_telegram_alert(self, title: str, message: str, data: Dict[str, Any]) -> bool:
        """Envía alerta por Telegram"""
        try:
            if not self.config.getboolean('telegram', 'enabled', fallback=False):
                return False
                
            bot_token = self.config.get('telegram', 'bot_token', fallback='')
            chat_ids = self.config.get('telegram', 'chat_ids', fallback='').split(',')
            parse_mode = self.config.get('telegram', 'parse_mode', fallback='HTML')
            disable_preview = self.config.getboolean('telegram', 'disable_web_page_preview', fallback=True)
            
            if not bot_token or not chat_ids[0]:
                self.logger.warning("Configuración de Telegram incompleta")
                return False
                
            # Formatear mensaje para Telegram
            formatted_message = self._format_telegram_message(title, message, data)
            
            success = True
            for chat_id in chat_ids:
                chat_id = chat_id.strip()
                if not chat_id:
                    continue
                    
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    'chat_id': chat_id,
                    'text': formatted_message,
                    'parse_mode': parse_mode,
                    'disable_web_page_preview': disable_preview
                }
                
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    self.logger.info(f"Telegram enviado a {chat_id}: {title}")
                else:
                    self.logger.error(f"Error Telegram {chat_id}: {response.status_code}")
                    success = False
                    
            return success
            
        except Exception as e:
            self.logger.error(f"Error enviando Telegram: {e}")
            return False
            
    def _format_telegram_message(self, title: str, message: str, data: Dict[str, Any]) -> str:
        """Formatea mensaje para Telegram con HTML"""
        severity = data.get('severity', 'MEDIUM')
        
        # Emojis según severidad
        severity_emojis = {
            'LOW': '🟢',
            'MEDIUM': '🟡',
            'HIGH': '🟠', 
            'CRITICAL': '🚨'
        }
        
        emoji = severity_emojis.get(severity, '⚠️')
        
        # Formatear mensaje con HTML
        formatted = f"{emoji} <b>{title}</b>\n\n"
        formatted += f"<b>Severidad:</b> {severity}\n"
        formatted += f"<b>Mensaje:</b> {message}\n"
        formatted += f"<b>Equipo:</b> {data.get('hostname', 'N/A')}\n"
        formatted += f"<b>Hora:</b> {data.get('timestamp', 'N/A')}\n"
        
        # Agregar detalles específicos según el tipo
        if data.get('type') == 'system_critical':
            formatted += f"\n🚨 <b>Evento Crítico de Sistema</b>\n"
            formatted += f"<b>Categoría:</b> {data.get('category', 'N/A')}\n"
            formatted += f"<b>Event ID:</b> {data.get('event_id', 'N/A')}\n"
            if data.get('shutdown_type'):
                formatted += f"<b>Tipo:</b> {data.get('shutdown_type', 'N/A')}\n"
        elif data.get('type') == 'suspicious_process':
            formatted += f"\n<b>Proceso:</b> {data.get('process_name', 'N/A')}\n"
            formatted += f"<b>PID:</b> {data.get('process_id', 'N/A')}\n"
        elif data.get('type') == 'suspicious_file':
            formatted += f"\n<b>Archivo:</b> {data.get('file_path', 'N/A')}\n"
            
        return formatted
    
    def _send_discord_alert(self, title: str, message: str, data: Dict[str, Any]) -> bool:
        """Envía alerta por Discord"""
        try:
            if not self.config.getboolean('discord', 'enabled', fallback=False):
                return False
                
            webhook_urls = self.config.get('discord', 'webhook_urls', fallback='').split(',')
            username = self.config.get('discord', 'username', fallback='Security Monitor')
            avatar_url = self.config.get('discord', 'avatar_url', fallback='')
            use_embeds = self.config.getboolean('discord', 'use_embeds', fallback=True)
            
            if not webhook_urls[0]:
                self.logger.warning("URLs de Discord webhook no configuradas")
                return False
                
            # Formatear mensaje para Discord
            if use_embeds:
                payload = self._format_discord_embed(title, message, data, username, avatar_url)
            else:
                payload = self._format_discord_message(title, message, data, username, avatar_url)
            
            success = True
            for webhook_url in webhook_urls:
                webhook_url = webhook_url.strip()
                if not webhook_url:
                    continue
                    
                response = requests.post(webhook_url, json=payload, timeout=10)
                
                if response.status_code == 204:  # Discord webhooks return 204 on success
                    self.logger.info(f"Discord enviado: {title}")
                else:
                    self.logger.error(f"Error Discord: {response.status_code}")
                    success = False
                    
            return success
            
        except Exception as e:
            self.logger.error(f"Error enviando Discord: {e}")
            return False
            
    def _format_discord_embed(self, title: str, message: str, data: Dict[str, Any], username: str, avatar_url: str) -> Dict:
        """Crea embed rico para Discord"""
        severity = data.get('severity', 'MEDIUM')
        
        # Colores según severidad (en decimal)
        severity_colors = {
            'LOW': 3066993,      # Verde
            'MEDIUM': 16776960,  # Amarillo
            'HIGH': 16744448,    # Naranja
            'CRITICAL': 15158332  # Rojo
        }
        
        color = severity_colors.get(severity, 10181046)  # Gris por defecto
        
        embed = {
            "title": f"🚨 {title}",
            "description": message,
            "color": color,
            "timestamp": data.get('timestamp', datetime.now().isoformat()),
            "fields": [
                {"name": "Severidad", "value": severity, "inline": True},
                {"name": "Equipo", "value": data.get('hostname', 'N/A'), "inline": True},
                {"name": "Usuario", "value": data.get('username', 'N/A'), "inline": True}
            ]
        }
        
        # Agregar campos específicos según el tipo
        if data.get('type') == 'system_critical':
            embed["fields"].extend([
                {"name": "Categoría", "value": data.get('category', 'N/A'), "inline": True},
                {"name": "Event ID", "value": str(data.get('event_id', 'N/A')), "inline": True},
                {"name": "Fuente", "value": data.get('source', 'N/A'), "inline": True}
            ])
        elif data.get('type') == 'suspicious_process':
            embed["fields"].extend([
                {"name": "Proceso", "value": data.get('process_name', 'N/A'), "inline": True},
                {"name": "PID", "value": str(data.get('process_id', 'N/A')), "inline": True}
            ])
        elif data.get('type') == 'suspicious_file':
            embed["fields"].append(
                {"name": "Archivo", "value": data.get('file_path', 'N/A'), "inline": False}
            )
            
        payload = {"embeds": [embed]}
        
        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url
            
        return payload
        
    def _format_discord_message(self, title: str, message: str, data: Dict[str, Any], username: str, avatar_url: str) -> Dict:
        """Crea mensaje simple para Discord"""
        severity = data.get('severity', 'MEDIUM')
        
        # Emojis según severidad
        severity_emojis = {
            'LOW': '🟢',
            'MEDIUM': '🟡',
            'HIGH': '🟠', 
            'CRITICAL': '🚨'
        }
        
        emoji = severity_emojis.get(severity, '⚠️')
        
        content = f"{emoji} **{title}**\n"
        content += f"**Severidad:** {severity}\n"
        content += f"**Mensaje:** {message}\n"
        content += f"**Equipo:** {data.get('hostname', 'N/A')}\n"
        content += f"**Hora:** {data.get('timestamp', 'N/A')}"
        
        payload = {"content": content}
        
        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url
            
        return payload
        
    def _send_slack_alert(self, title: str, message: str, data: Dict[str, Any]) -> bool:
        """Envía alerta por Slack (versión mejorada)"""
        try:
            if not self.config.getboolean('slack', 'enabled', fallback=False):
                return False
                
            webhook_urls = self.config.get('slack', 'webhook_urls', fallback='').split(',')
            channel = self.config.get('slack', 'channel', fallback='')
            username = self.config.get('slack', 'username', fallback='Security Monitor')
            icon_emoji = self.config.get('slack', 'icon_emoji', fallback=':warning:')
            use_attachments = self.config.getboolean('slack', 'use_attachments', fallback=True)
            
            if not webhook_urls[0]:
                self.logger.warning("URLs de Slack webhook no configuradas")
                return False
                
            # Formatear mensaje para Slack
            if use_attachments:
                payload = self._format_slack_message_improved(title, message, data, channel, username, icon_emoji)
            else:
                payload = self._format_slack_message(title, message, data)
            
            success = True
            for webhook_url in webhook_urls:
                webhook_url = webhook_url.strip()
                if not webhook_url:
                    continue
                    
                response = requests.post(webhook_url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    self.logger.info(f"Slack enviado: {title}")
                else:
                    self.logger.error(f"Error Slack: {response.status_code}")
                    success = False
                    
            return success
            
        except Exception as e:
            self.logger.error(f"Error enviando Slack: {e}")
            return False
            
    def _format_slack_message_improved(self, title: str, message: str, data: Dict[str, Any], channel: str, username: str, icon_emoji: str) -> Dict:
        """Formatea mensaje mejorado para Slack con attachments"""
        severity = data.get('severity', 'MEDIUM')
        
        # Colores según severidad
        severity_colors = {
            'LOW': 'good',
            'MEDIUM': 'warning',
            'HIGH': 'danger', 
            'CRITICAL': 'danger'
        }
        
        color = severity_colors.get(severity, 'warning')
        
        # Crear attachment principal
        attachment = {
            "color": color,
            "title": f"🚨 {title}",
            "text": message,
            "fields": [
                {"title": "Severidad", "value": severity, "short": True},
                {"title": "Equipo", "value": data.get('hostname', 'N/A'), "short": True},
                {"title": "Hora", "value": data.get('timestamp', 'N/A'), "short": False}
            ],
            "footer": "Sistema de Monitoreo de Seguridad",
            "ts": int(datetime.now().timestamp())
        }
        
        # Agregar campos específicos según el tipo
        if data.get('type') == 'system_critical':
            attachment["fields"].extend([
                {"title": "Categoría", "value": data.get('category', 'N/A'), "short": True},
                {"title": "Event ID", "value": str(data.get('event_id', 'N/A')), "short": True}
            ])
        elif data.get('type') == 'suspicious_process':
            attachment["fields"].extend([
                {"title": "Proceso", "value": data.get('process_name', 'N/A'), "short": True},
                {"title": "PID", "value": str(data.get('process_id', 'N/A')), "short": True}
            ])
        elif data.get('type') == 'suspicious_file':
            attachment["fields"].append(
                {"title": "Archivo", "value": data.get('file_path', 'N/A'), "short": False}
            )
            
        payload = {
            "attachments": [attachment]
        }
        
        if channel:
            payload["channel"] = channel
        if username:
            payload["username"] = username
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji
            
        return payload
            
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
        
    def _send_whatsapp_alert(self, title: str, message: str, data: Dict[str, Any]) -> bool:
        """Envía alerta por WhatsApp Business API"""
        try:
            if not self.config.getboolean('whatsapp', 'enabled', fallback=False):
                return False
                
            api_endpoint = self.config.get('whatsapp', 'api_endpoint', fallback='')
            access_token = self.config.get('whatsapp', 'access_token', fallback='')
            phone_numbers = self.config.get('whatsapp', 'phone_numbers', fallback='').split(',')
            use_templates = self.config.getboolean('whatsapp', 'use_templates', fallback=False)
            template_name = self.config.get('whatsapp', 'template_name', fallback='security_alert')
            
            if not api_endpoint or not access_token or not phone_numbers[0]:
                self.logger.warning("Configuración de WhatsApp incompleta")
                return False
                
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Formatear mensaje para WhatsApp
            formatted_message = self._format_whatsapp_message(title, message, data)
            
            success = True
            for phone_number in phone_numbers:
                phone_number = phone_number.strip()
                if not phone_number:
                    continue
                    
                if use_templates:
                    # Payload para template
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": phone_number,
                        "type": "template",
                        "template": {
                            "name": template_name,
                            "language": {"code": "es"},
                            "components": [{
                                "type": "body",
                                "parameters": [
                                    {"type": "text", "text": title},
                                    {"type": "text", "text": formatted_message}
                                ]
                            }]
                        }
                    }
                else:
                    # Payload para mensaje de texto
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": phone_number,
                        "type": "text",
                        "text": {"body": formatted_message}
                    }
                
                response = requests.post(api_endpoint, json=payload, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.logger.info(f"WhatsApp enviado a {phone_number}: {title}")
                else:
                    self.logger.error(f"Error WhatsApp {phone_number}: {response.status_code}")
                    success = False
                    
            return success
            
        except Exception as e:
            self.logger.error(f"Error enviando WhatsApp: {e}")
            return False
            
    def _format_whatsapp_message(self, title: str, message: str, data: Dict[str, Any]) -> str:
        """Formatea mensaje para WhatsApp"""
        severity = data.get('severity', 'MEDIUM')
        
        # Emojis según severidad
        severity_emojis = {
            'LOW': '🟢',
            'MEDIUM': '🟡',
            'HIGH': '🟠', 
            'CRITICAL': '🚨'
        }
        
        emoji = severity_emojis.get(severity, '⚠️')
        
        # Formatear mensaje
        formatted = f"{emoji} *{title}*\n\n"
        formatted += f"*Severidad:* {severity}\n"
        formatted += f"*Mensaje:* {message}\n"
        formatted += f"*Equipo:* {data.get('hostname', 'N/A')}\n"
        formatted += f"*Hora:* {data.get('timestamp', 'N/A')}\n"
        
        # Agregar detalles específicos según el tipo
        if data.get('type') == 'system_critical':
            formatted += f"\n🚨 *Evento Crítico de Sistema*\n"
            formatted += f"*Categoría:* {data.get('category', 'N/A')}\n"
            formatted += f"*Event ID:* {data.get('event_id', 'N/A')}\n"
        elif data.get('type') == 'suspicious_process':
            formatted += f"\n*Proceso:* {data.get('process_name', 'N/A')}\n"
            formatted += f"*PID:* {data.get('process_id', 'N/A')}\n"
        elif data.get('type') == 'suspicious_file':
            formatted += f"\n*Archivo:* {data.get('file_path', 'N/A')}\n"
            
        return formatted
        
    def _send_teams_alert(self, title: str, message: str, data: Dict[str, Any]) -> bool:
        """Envía alerta por Microsoft Teams"""
        try:
            if not self.config.getboolean('teams', 'enabled', fallback=False):
                return False
                
            webhook_urls = self.config.get('teams', 'webhook_urls', fallback='').split(',')
            use_adaptive_cards = self.config.getboolean('teams', 'use_adaptive_cards', fallback=True)
            theme_color = self.config.get('teams', 'theme_color', fallback='FF6B35')
            card_title = self.config.get('teams', 'card_title', fallback='Alerta de Seguridad')
            
            if not webhook_urls[0]:
                self.logger.warning("URLs de Teams webhook no configuradas")
                return False
                
            # Formatear mensaje para Teams
            if use_adaptive_cards:
                payload = self._format_teams_adaptive_card(title, message, data, theme_color, card_title)
            else:
                payload = self._format_teams_message(title, message, data, theme_color)
            
            success = True
            for webhook_url in webhook_urls:
                webhook_url = webhook_url.strip()
                if not webhook_url:
                    continue
                    
                response = requests.post(webhook_url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    self.logger.info(f"Teams enviado: {title}")
                else:
                    self.logger.error(f"Error Teams: {response.status_code}")
                    success = False
                    
            return success
            
        except Exception as e:
            self.logger.error(f"Error enviando Teams: {e}")
            return False
            
    def _format_teams_adaptive_card(self, title: str, message: str, data: Dict[str, Any], theme_color: str, card_title: str) -> Dict:
        """Crea tarjeta adaptativa para Microsoft Teams"""
        severity = data.get('severity', 'MEDIUM')
        
        # Colores según severidad
        severity_colors = {
            'LOW': '28A745',
            'MEDIUM': 'FFC107',
            'HIGH': 'FD7E14',
            'CRITICAL': 'DC3545'
        }
        
        color = severity_colors.get(severity, theme_color)
        
        card = {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "body": [
                        {
                            "type": "TextBlock",
                            "size": "Medium",
                            "weight": "Bolder",
                            "text": f"🚨 {title}",
                            "color": "Attention"
                        },
                        {
                            "type": "TextBlock",
                            "text": message,
                            "wrap": True
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Severidad", "value": severity},
                                {"title": "Equipo", "value": data.get('hostname', 'N/A')},
                                {"title": "Hora", "value": data.get('timestamp', 'N/A')}
                            ]
                        }
                    ],
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.2"
                }
            }]
        }
        
        # Agregar hechos específicos según el tipo
        if data.get('type') == 'system_critical':
            card["attachments"][0]["content"]["body"][2]["facts"].extend([
                {"title": "Categoría", "value": data.get('category', 'N/A')},
                {"title": "Event ID", "value": str(data.get('event_id', 'N/A'))}
            ])
        elif data.get('type') == 'suspicious_process':
            card["attachments"][0]["content"]["body"][2]["facts"].extend([
                {"title": "Proceso", "value": data.get('process_name', 'N/A')},
                {"title": "PID", "value": str(data.get('process_id', 'N/A'))}
            ])
        elif data.get('type') == 'suspicious_file':
            card["attachments"][0]["content"]["body"][2]["facts"].append(
                {"title": "Archivo", "value": data.get('file_path', 'N/A')}
            )
            
        return card
        
    def _format_teams_message(self, title: str, message: str, data: Dict[str, Any], theme_color: str) -> Dict:
        """Crea mensaje simple para Microsoft Teams"""
        severity = data.get('severity', 'MEDIUM')
        
        # Colores según severidad
        severity_colors = {
            'LOW': '28A745',
            'MEDIUM': 'FFC107',
            'HIGH': 'FD7E14',
            'CRITICAL': 'DC3545'
        }
        
        color = severity_colors.get(severity, theme_color)
        
        return {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": color,
            "summary": title,
            "sections": [{
                "activityTitle": f"🚨 {title}",
                "activitySubtitle": f"Severidad: {severity}",
                "text": message,
                "facts": [
                    {"name": "Equipo", "value": data.get('hostname', 'N/A')},
                    {"name": "Usuario", "value": data.get('username', 'N/A')},
                    {"name": "Hora", "value": data.get('timestamp', 'N/A')}
                ]
            }]
        }
        
    def _send_pushover_alert(self, title: str, message: str, data: Dict[str, Any]) -> bool:
        """Envía alerta por Pushover"""
        try:
            if not self.config.getboolean('pushover', 'enabled', fallback=False):
                return False
                
            app_token = self.config.get('pushover', 'app_token', fallback='')
            user_key = self.config.get('pushover', 'user_key', fallback='')
            priority = self.config.getint('pushover', 'priority', fallback=1)
            sound = self.config.get('pushover', 'sound', fallback='siren')
            
            if not app_token or not user_key:
                self.logger.warning("Configuración de Pushover incompleta")
                return False
                
            # Formatear mensaje para Pushover
            formatted_message = self._format_pushover_message(title, message, data)
            
            payload = {
                'token': app_token,
                'user': user_key,
                'title': title,
                'message': formatted_message,
                'priority': priority,
                'sound': sound
            }
            
            # Configuración especial para prioridad de emergencia
            if priority == 2:
                payload['retry'] = 60  # Reintentar cada 60 segundos
                payload['expire'] = 3600  # Expirar después de 1 hora
            
            response = requests.post('https://api.pushover.net/1/messages.json', data=payload, timeout=10)
            
            if response.status_code == 200:
                self.logger.info(f"Pushover enviado: {title}")
                return True
            else:
                self.logger.error(f"Error Pushover: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error enviando Pushover: {e}")
            return False
            
    def _format_pushover_message(self, title: str, message: str, data: Dict[str, Any]) -> str:
        """Formatea mensaje para Pushover"""
        severity = data.get('severity', 'MEDIUM')
        
        formatted = f"{message}\n\n"
        formatted += f"Severidad: {severity}\n"
        formatted += f"Equipo: {data.get('hostname', 'N/A')}\n"
        formatted += f"Hora: {data.get('timestamp', 'N/A')}"
        
        # Agregar detalles específicos según el tipo
        if data.get('type') == 'system_critical':
            formatted += f"\n\nEvento Crítico:\nCategoría: {data.get('category', 'N/A')}\nEvent ID: {data.get('event_id', 'N/A')}"
        elif data.get('type') == 'suspicious_process':
            formatted += f"\n\nProceso: {data.get('process_name', 'N/A')}\nPID: {data.get('process_id', 'N/A')}"
        elif data.get('type') == 'suspicious_file':
            formatted += f"\n\nArchivo: {data.get('file_path', 'N/A')}"
            
        return formatted
        
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
    
    def test_all_channels():
        """Prueba todas las plataformas de alertas"""
        alert_manager = AlertManager()
        
        # Diferentes tipos de pruebas
        test_cases = [
            {
                'title': 'Prueba Sistema General',
                'message': 'Prueba del sistema de alertas - Funcionalidad básica',
                'data': {
                    'type': 'system_alert',
                    'severity': 'HIGH',
                    'hostname': 'TEST-PC'
                }
            },
            {
                'title': 'Evento Crítico de Sistema',
                'message': 'Simulación de evento crítico detectado',
                'data': {
                    'type': 'system_critical',
                    'severity': 'CRITICAL',
                    'category': 'Sistema',
                    'event_id': 1074,
                    'source': 'System',
                    'source_name': 'USER32',
                    'description': 'Apagado iniciado por usuario'
                }
            },
            {
                'title': 'Proceso Sospechoso',
                'message': 'Proceso potencialmente malicioso detectado',
                'data': {
                    'type': 'suspicious_process',
                    'severity': 'HIGH',
                    'process_name': 'malware.exe',
                    'process_id': 1234,
                    'executable_path': 'C:\\temp\\malware.exe',
                    'reason': 'Nombre de proceso en lista negra'
                }
            },
            {
                'title': 'Archivo Sospechoso',
                'message': 'Archivo con patrones maliciosos detectado',
                'data': {
                    'type': 'suspicious_file',
                    'severity': 'MEDIUM',
                    'file_path': 'C:\\Users\\test\\Downloads\\suspicious.exe',
                    'action': 'creado'
                }
            }
        ]
        
        print("=== PRUEBA DEL SISTEMA DE ALERTAS MEJORADO ===\n")
        
        overall_success = True
        for i, test_case in enumerate(test_cases, 1):
            print(f"Ejecutando prueba {i}/4: {test_case['title']}")
            
            success = alert_manager.send_alert(
                test_case['title'],
                test_case['message'],
                test_case['data']
            )
            
            status = "✅ EXITOSA" if success else "❌ FALLIDA"
            print(f"Resultado: {status}\n")
            
            if not success:
                overall_success = False
        
        print("=== RESUMEN DE CONFIGURACIÓN ===")
        print(f"Email: {'✅' if alert_manager.config.get('alerts', 'email_username', fallback='') else '❌'}")
        print(f"Webhook genérico: {'✅' if alert_manager.config.get('alerts', 'webhook_url', fallback='') else '❌'}")
        print(f"Telegram: {'✅' if alert_manager.config.getboolean('telegram', 'enabled', fallback=False) else '❌'}")
        print(f"Discord: {'✅' if alert_manager.config.getboolean('discord', 'enabled', fallback=False) else '❌'}")
        print(f"Slack: {'✅' if alert_manager.config.getboolean('slack', 'enabled', fallback=False) else '❌'}")
        print(f"WhatsApp: {'✅' if alert_manager.config.getboolean('whatsapp', 'enabled', fallback=False) else '❌'}")
        print(f"Microsoft Teams: {'✅' if alert_manager.config.getboolean('teams', 'enabled', fallback=False) else '❌'}")
        print(f"Pushover: {'✅' if alert_manager.config.getboolean('pushover', 'enabled', fallback=False) else '❌'}")
        print(f"Notificaciones Windows: {'✅' if PLYER_AVAILABLE or WIN32_AVAILABLE else '❌'}")
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"{'✅ TODAS LAS PRUEBAS EXITOSAS' if overall_success else '❌ ALGUNAS PRUEBAS FALLARON'}")
        print("\nNota: Las pruebas pueden fallar si las plataformas no están configuradas.")
        print("Revisa config.ini y configura las credenciales necesarias.")
        
        return overall_success
    
    def test_specific_platform(platform):
        """Prueba una plataforma específica"""
        alert_manager = AlertManager()
        
        # Temporalmente cambiar método de alerta
        original_method = alert_manager.alert_methods
        alert_manager.alert_methods = platform
        
        test_data = {
            'type': 'system_alert',
            'severity': 'HIGH',
            'hostname': 'TEST-PC'
        }
        
        print(f"Probando {platform.upper()}...")
        success = alert_manager.send_alert(
            f"Prueba {platform.upper()}",
            f"Mensaje de prueba para {platform}",
            test_data
        )
        
        # Restaurar método original
        alert_manager.alert_methods = original_method
        
        print(f"Resultado: {'✅ EXITOSA' if success else '❌ FALLIDA'}")
        return success
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            # Prueba completa de todas las plataformas
            test_all_channels()
            
        elif command in ['telegram', 'discord', 'slack', 'whatsapp', 'teams', 'pushover', 'email', 'webhook', 'notification']:
            # Prueba de plataforma específica
            test_specific_platform(command)
            
        elif command == 'help':
            print("=== SISTEMA DE ALERTAS - AYUDA ===")
            print("Uso: python quadient_sender_simple.py [comando]")
            print("")
            print("Comandos disponibles:")
            print("  test          - Prueba todas las plataformas configuradas")
            print("  telegram      - Prueba solo Telegram")
            print("  discord       - Prueba solo Discord") 
            print("  slack         - Prueba solo Slack")
            print("  whatsapp      - Prueba solo WhatsApp Business API")
            print("  teams         - Prueba solo Microsoft Teams")
            print("  pushover      - Prueba solo Pushover")
            print("  email         - Prueba solo Email")
            print("  webhook       - Prueba solo webhook genérico")
            print("  notification  - Prueba solo notificaciones Windows")
            print("  help          - Muestra esta ayuda")
            print("")
            print("Configuración:")
            print("- Edita config.ini para configurar cada plataforma")
            print("- Habilita las plataformas que quieras usar")
            print("- Configura credenciales y URLs según corresponda")
            
        else:
            print(f"Comando desconocido: {command}")
            print("Usa 'python quadient_sender_simple.py help' para ver comandos disponibles")
    else:
        print("Sistema de Alertas Multi-Plataforma")
        print("Usa 'python quadient_sender_simple.py help' para ver opciones")