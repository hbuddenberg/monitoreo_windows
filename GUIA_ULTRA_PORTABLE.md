# 🔐 Monitor Ultra Portable de Eventos Windows

## ⚡ Versión SIN Permisos Administrativos

Esta es la versión **más portable** del monitor que funciona **completamente sin permisos administrativos** y con **mínimas dependencias**.

---

## 🎯 **Características Principales**

### ✅ **Completamente Portable**
- ✅ **NO requiere permisos administrativos**
- ✅ **NO requiere instalaciones**  
- ✅ **Solo necesita Python estándar**
- ✅ **Funciona desde cualquier carpeta**
- ✅ **No deja rastros en el sistema**

### 🔍 **Qué Monitorea**
- 🚨 **Procesos sospechosos** (malware, virus, trojans)
- 📁 **Archivos sospechosos** en carpetas del usuario
- 🌐 **Conexiones de red sospechosas** (puertos maliciosos)
- 💾 **Alto uso de CPU/Memoria**
- 📂 **Nuevos archivos ejecutables**

### 📧 **Sistemas de Alerta**
- 🪟 **Notificaciones de Windows** (automáticas)
- 📧 **Email** (opcional)
- 🔗 **Webhooks** (Slack, Discord, etc.)
- 📄 **Archivos de alerta** en el escritorio
- 📝 **Logs detallados**

---

## 🚀 **Opciones de Uso**

### **Opción 1: Ultra Simple (Solo Python del Sistema)**
```cmd
# Si Python ya está instalado:
python monitor_ultra_portable.py

# Con configuración de email/webhook:
python monitor_ultra_portable.py --setup
```

### **Opción 2: Ejecutable Simple**
```cmd
# Doble clic en:
MONITOR_ULTRA_PORTABLE.bat
```

### **Opción 3: Versión Completa Portable**
```cmd
# Crea carpeta completa con Python embebido:
CREAR_PORTABLE_COMPLETO.bat
```

---

## 📋 **Guía de Instalación**

### **Paso 1: Verificar Python**
El monitor funciona con cualquier Python 3.6+:

- ✅ **Python preinstalado** en Windows 10/11
- ✅ **Python de Microsoft Store** (no requiere admin)
- ✅ **Python portable** (PortableApps, WinPython, etc.)
- ✅ **Python embebido** (incluido en versión completa)

### **Paso 2: Usar el Monitor**

#### **Uso Inmediato:**
1. Copie `monitor_ultra_portable.py` a cualquier carpeta
2. Ejecute: `python monitor_ultra_portable.py`
3. ¡Listo! El monitor funcionará inmediatamente

#### **Con Configuración:**
1. Ejecute: `python monitor_ultra_portable.py --setup`
2. Configure email (opcional)
3. Configure webhook (opcional)
4. El monitor iniciará automáticamente

---

## ⚙️ **Configuración**

### **Email (Gmail)**
```
Email para alertas: tu_email@gmail.com
Password del email: tu_password_app
Email destino: admin@empresa.com
```

### **Webhook (Slack)**
```
URL de webhook: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### **Personalización en el Código**
```python
# Edite estas variables en monitor_ultra_portable.py:
'suspicious_processes': [
    'malware.exe', 'virus.exe', 'trojan.exe', 
    'keylogger.exe', 'hack.exe'
],
'monitor_dirs': [
    '~/Desktop', '~/Downloads', '~/Documents'
],
'check_interval': 30  # Segundos
```

---

## 🛡️ **Detección Específica**

### **Procesos Monitoreados**
- `malware.exe`, `virus.exe`, `trojan.exe`
- `keylogger.exe`, `hack.exe`, `crack.exe`
- `suspicious.exe`, `backdoor.exe`
- **Personalizable** en el código

### **Archivos Monitoreados**
- Archivos con nombres sospechosos
- Ejecutables en carpetas temporales
- Scripts maliciosos (`.bat`, `.ps1`, `.vbs`)

### **Red Monitoreada**
- Puertos sospechosos: `4444, 5555, 6666, 7777, 31337`
- Conexiones no autorizadas
- **Completamente pasivo** (solo observa)

---

## 📊 **Tipos de Alerta**

### **🔴 CRÍTICO**
- Proceso malicioso detectado
- Conexión a puerto de backdoor

### **🟡 ALTO**
- Archivo sospechoso creado
- Puerto sospechoso en uso
- Alto uso de CPU (>95%)

### **🔵 MEDIO**
- Archivo ejecutable sospechoso
- Actividad inusual de red

---

## 📁 **Estructura de Archivos**

### **Versión Mínima**
```
📁 Cualquier carpeta/
├── 📄 monitor_ultra_portable.py    # Archivo principal
└── 📄 MONITOR_ULTRA_PORTABLE.bat   # Launcher opcional
```

### **Versión Completa (con CREAR_PORTABLE_COMPLETO.bat)**
```
📁 PORTABLE_MONITOR/
├── 📁 python-embedded/             # Python completo incluido
├── 📄 portable_monitor.py          # Monitor con más funciones
├── 📄 config.ini                   # Configuración
├── 📁 logs/                        # Logs del sistema
├── 🚀 EJECUTAR_MONITOR_PORTABLE.bat # Ejecutar
└── 📖 README_PORTABLE.txt          # Documentación
```

---

## 🔧 **Solución de Problemas**

### **"Python no encontrado"**
```cmd
# Opciones:
1. Instalar Python desde Microsoft Store (no requiere admin)
2. Usar Python portable
3. Usar la versión completa con Python embebido
```

### **"No se pueden enviar emails"**
```python
# Configurar Gmail con password de aplicación:
1. Activar autenticación de 2 factores
2. Generar password de aplicación
3. Usar ese password en el monitor
```

### **"No aparecen notificaciones"**
```cmd
# El monitor usa múltiples métodos:
1. msg command (Windows estándar)
2. PowerShell notifications
3. Archivos en el escritorio como respaldo
```

---

## 🚨 **Limitaciones de la Versión Sin Permisos Admin**

### **❌ No Disponible:**
- Acceso a **Event Log de Windows** (requiere permisos admin)
- Monitoreo de **servicios del sistema**
- Acceso a **archivos de sistema protegidos**
- **Instalación como servicio**

### **✅ Sí Disponible:**
- Monitoreo de **procesos de usuario**
- Archivos en **carpetas del usuario**
- **Conexiones de red visibles al usuario**
- **Métricas básicas del sistema**
- **Alertas múltiples**

---

## 💡 **Casos de Uso Ideales**

### **🏢 Entornos Corporativos**
- Equipos sin permisos administrativos
- Monitoreo básico de seguridad
- Detección de malware en carpetas de usuario

### **🏠 Uso Personal**
- Equipos compartidos
- Monitoreo temporal
- Análisis rápido de seguridad

### **🔧 Análisis Forense**
- Investigación inicial
- Detección rápida de amenazas
- Monitoreo sin alterar el sistema

---

## 📞 **Soporte y Personalización**

### **Personalizar Detección**
Edite las listas en `monitor_ultra_portable.py`:
```python
'suspicious_processes': ['tu_proceso.exe'],
'suspicious_files': ['tu_patron'],
'monitor_dirs': ['tu_directorio']
```

### **Agregar Nuevas Alertas**
```python
# En _monitor_processes():
if 'tu_proceso' in proc_name:
    self._send_alert("Título", "Mensaje", "CRITICAL")
```

### **Cambiar Intervalos**
```python
'check_interval': 30,  # Segundos entre verificaciones
```

---

## 🏆 **Ventajas Principales**

1. **🚀 Instalación Instantánea** - Copia y ejecuta
2. **🔐 Sin Permisos Admin** - Funciona en cualquier equipo
3. **📱 Ultra Ligero** - Solo Python estándar
4. **🔔 Alertas Múltiples** - Email, webhook, notificaciones
5. **📝 Logs Detallados** - Registro completo de actividad
6. **🛡️ Detección Eficaz** - Malware común y amenazas
7. **⚙️ Personalizable** - Fácil de modificar

---

¡El Monitor Ultra Portable está listo para proteger cualquier equipo Windows sin restricciones de permisos!