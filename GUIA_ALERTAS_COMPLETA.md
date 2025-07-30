# Guía Completa del Sistema de Alertas Multi-Plataforma

## 🚀 Introducción

El sistema de monitoreo de Windows ahora incluye un sistema de alertas avanzado que puede enviar notificaciones a **9 plataformas diferentes**:

- ✅ **Slack** (Configurado)
- 📧 **Email** 
- 📱 **Telegram**
- 💬 **Discord**
- 📞 **WhatsApp Business API**
- 👥 **Microsoft Teams**
- 📮 **Pushover**
- 🌐 **Webhooks Genéricos**
- 🖥️ **Notificaciones Windows**

---

## 📋 Configuración Rápida

### 1. **Slack** ✅ (Ya configurado)
```ini
[slack]
enabled = true
webhook_urls = https://hooks.slack.com/services/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
channel = #security-alerts
username = Security Monitor
icon_emoji = :warning:
use_attachments = true
```

### 2. **Telegram**
```ini
[telegram]
enabled = true
bot_token = TU_BOT_TOKEN_AQUI
chat_ids = TU_CHAT_ID_AQUI,OTRO_CHAT_ID
parse_mode = HTML
```
**Cómo obtener:**
1. Habla con @BotFather en Telegram
2. Crea un bot con `/newbot`
3. Obtén el token
4. Envía un mensaje al bot y ve a `https://api.telegram.org/botTU_TOKEN/getUpdates` para obtener el chat_id

### 3. **Discord**
```ini
[discord]
enabled = true
webhook_urls = TU_DISCORD_WEBHOOK_URL
username = Security Monitor
use_embeds = true
```
**Cómo obtener:**
1. Ve a configuración del servidor → Integraciones → Webhooks
2. Crea un nuevo webhook
3. Copia la URL

### 4. **WhatsApp Business API**
```ini
[whatsapp]
enabled = true
api_endpoint = https://graph.facebook.com/v17.0/TU_PHONE_NUMBER_ID/messages
access_token = TU_ACCESS_TOKEN
phone_numbers = +1234567890,+0987654321
```
**Requisitos:**
- Cuenta de WhatsApp Business API
- Meta for Developers account
- Verificación de números de teléfono

### 5. **Microsoft Teams**
```ini
[teams]
enabled = true
webhook_urls = TU_TEAMS_WEBHOOK_URL
use_adaptive_cards = true
theme_color = FF6B35
```
**Cómo obtener:**
1. Ve al canal de Teams → Configuración → Conectores
2. Busca "Incoming Webhook"
3. Configura y copia la URL

### 6. **Pushover**
```ini
[pushover]
enabled = true
app_token = TU_APP_TOKEN
user_key = TU_USER_KEY
priority = 1
sound = siren
```
**Cómo obtener:**
1. Crea cuenta en pushover.net
2. Registra una aplicación
3. Obtén app token y user key

### 7. **Email**
```ini
[alerts]
smtp_server = smtp.gmail.com
smtp_port = 587
email_username = tu_email@gmail.com
email_password = tu_password_app
email_from = tu_email@gmail.com
email_to = admin@empresa.com,security@empresa.com
```

---

## 🧪 Comandos de Prueba

### Probar Todo el Sistema
```bash
python quadient_sender_simple.py test
```

### Probar Plataformas Específicas
```bash
# Plataformas principales
python quadient_sender_simple.py slack
python quadient_sender_simple.py telegram
python quadient_sender_simple.py discord
python quadient_sender_simple.py teams

# Otras plataformas
python quadient_sender_simple.py whatsapp
python quadient_sender_simple.py pushover
python quadient_sender_simple.py email
python quadient_sender_simple.py webhook
python quadient_sender_simple.py notification

# Ver ayuda
python quadient_sender_simple.py help
```

---

## 🎨 Formatos de Mensaje por Plataforma

### **Slack**
- ✅ Attachments con colores
- ✅ Campos estructurados
- ✅ Emojis según severidad
- ✅ Timestamp

### **Telegram**
- ✅ HTML formatting
- ✅ Negrita y emojis
- ✅ Detalles específicos por tipo
- ✅ Sin preview de enlaces

### **Discord**
- ✅ Embeds ricos con colores
- ✅ Campos inline
- ✅ Timestamp automático
- ✅ Username personalizable

### **Microsoft Teams**
- ✅ Adaptive Cards
- ✅ FactSet estructurado
- ✅ Colores por severidad
- ✅ Formato profesional

### **WhatsApp**
- ✅ Formato Markdown
- ✅ Soporte para templates
- ✅ Múltiples números
- ✅ Emojis según severidad

### **Pushover**
- ✅ Prioridades configurables
- ✅ Sonidos personalizados
- ✅ Reintentos automáticos
- ✅ Expiración de mensajes

---

## ⚙️ Configuración Avanzada

### Control de Severidad
```ini
[alerts]
min_severity = MEDIUM  # LOW, MEDIUM, HIGH, CRITICAL
alert_cooldown = 300   # segundos entre alertas duplicadas
```

### Múltiples Destinos
Todas las plataformas soportan múltiples destinos separados por comas:
```ini
webhook_urls = URL1,URL2,URL3
chat_ids = CHAT1,CHAT2,CHAT3  
phone_numbers = +123456789,+987654321
```

### Filtros y Umbrales
```ini
[thresholds]
max_events_per_minute = 10
max_suspicious_processes = 3
max_file_changes_per_minute = 50
```

---

## 🔍 Tipos de Alertas Soportados

### 1. **Eventos Críticos del Sistema**
- Apagados inesperados
- Fallos del kernel
- Servicios críticos detenidos

### 2. **Procesos Sospechosos**
- Malware detectado
- Procesos en ubicaciones sospechosas
- Alto uso de recursos

### 3. **Archivos Sospechosos**
- Archivos con patrones maliciosos
- Cambios en archivos críticos
- Alta entropía (posible cifrado)

### 4. **Eventos de Seguridad**
- Intentos de login fallidos
- Cambios de privilegios
- Accesos no autorizados

---

## 🛠️ Integración con el Monitor

El sistema de alertas se integra automáticamente con:

- `windows_event_monitor.py` - Monitor principal
- `monitor_ultra_portable.py` - Versión portable
- Cualquier script que use `send_alert()`

### Ejemplo de Uso en Código
```python
from quadient_sender_simple import send_alert

# Enviar alerta simple
send_alert("Título", "Mensaje", {
    'type': 'system_critical',
    'severity': 'HIGH',
    'hostname': 'SERVER-01'
})
```

---

## 🔒 Seguridad y Mejores Prácticas

### Protección de Credenciales
- ✅ Nunca commitear tokens reales
- ✅ Usar variables de entorno en producción
- ✅ Rotar tokens periódicamente
- ✅ Usar permisos mínimos necesarios

### Rate Limiting
- ✅ Cooldown entre alertas duplicadas
- ✅ Respeto a límites de API
- ✅ Manejo de errores 429 (Too Many Requests)

### Logging
- ✅ Todos los envíos se registran en `logs/alerts.log`
- ✅ Errores detallados para debugging
- ✅ Historial JSON opcional

---

## 🚨 Solución de Problemas

### Alertas No Llegan
1. Verificar configuración en `config.ini`
2. Comprobar que `enabled = true`
3. Validar credenciales y URLs
4. Revisar logs en `logs/alerts.log`
5. Probar con `python quadient_sender_simple.py PLATAFORMA`

### Errores Comunes
- **403 Forbidden**: Token o credenciales incorrectas
- **404 Not Found**: URL de webhook incorrecta
- **429 Too Many Requests**: Rate limiting, reducir frecuencia
- **Timeout**: Problemas de conexión, verificar red

### Verificación de Estado
```bash
# Ver estado de todas las plataformas
python quadient_sender_simple.py test

# Ver configuración actual
grep -A 5 "\\[telegram\\|\\[discord\\|\\[slack\\]" config.ini
```

---

## 📈 Próximas Funcionalidades

- 🔄 **Retry automático** con backoff exponencial
- 📊 **Dashboard web** para monitoreo de estado
- 🔔 **Escalamiento** automático por severidad
- 📝 **Templates** personalizables por evento
- 🌍 **Soporte i18n** (múltiples idiomas)

---

## 🎯 Estado Actual

✅ **Funcionando perfectamente:**
- Slack (configurado y probado)
- Arquitectura multi-plataforma
- Sistema de pruebas completo
- Formateo inteligente por plataforma

⚙️ **Listo para configurar:**
- Telegram, Discord, Teams, WhatsApp, Pushover
- Solo necesitan credenciales

🔧 **Sistema robusto con:**
- Manejo de errores
- Logging completo  
- Rate limiting
- Compatibilidad total con monitor existente

---

*El sistema está listo para usar en producción con Slack, y puede expandirse fácilmente a las otras 8 plataformas según necesidades.*