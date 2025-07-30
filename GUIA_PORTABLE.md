# Guía de Instalación Portable del Sistema de Monitoreo de Eventos Windows

Esta guía explica cómo instalar y usar el **Sistema Completo de Monitoreo de Eventos** en un sistema Windows **sin necesidad de tener Python preinstalado**.

## 🆕 Nuevas Características

- **Monitoreo de Event Log de Windows**: Detecta eventos críticos del sistema
- **Monitoreo de Procesos Sospechosos**: Identifica malware y procesos maliciosos
- **Análisis de Archivos**: Detecta código malicioso y patrones sospechosos
- **Sistema de Alertas Mejorado**: Email, webhooks, notificaciones Windows
- **Detección de Códigos Específicos**: Análisis avanzado de patrones maliciosos

## Instalación Rápida

1. Ejecute el archivo `INSTALAR_PORTABLE.bat` (con doble clic)
2. Siga las instrucciones en pantalla
3. ¡Listo! El sistema se configurará automáticamente

## ¿Qué hace el instalador?

El instalador automático `INSTALAR_PORTABLE.bat` realizará las siguientes acciones:

1. **Descarga Python Embebido**: Obtiene una versión portable de Python que no requiere instalación
2. **Configura Python**: Lo configura para que funcione correctamente con el monitor
3. **Instala Dependencias**: Instala las librerías necesarias para el funcionamiento del sistema
4. **Crea Scripts de Ejecución**: Genera scripts para ejecutar el monitor fácilmente
5. **Configura Inicio Automático**: Opcionalmente, configura el monitor para iniciarse con Windows

## Ejecutar el Sistema de Monitoreo

Después de la instalación, puede ejecutar diferentes tipos de monitoreo:

### Ejecución Manual

1. **Monitor Interactivo**: Ejecute `ejecutar_monitor_portable.bat`
   - Opción 1: Monitor de Sesión (original)
   - Opción 2: Monitor de Eventos Windows (nuevo)
   - Opción 3: Monitor Completo (ambos sistemas)

2. **Monitor en Segundo Plano**: Ejecute `ejecutar_monitor_portable_background.ps1`

### Tipos de Monitoreo Disponibles

- **Monitor de Sesión**: Monitoreo básico de sesiones de servidor
- **Monitor de Eventos**: Monitoreo avanzado de eventos Windows, procesos y archivos
- **Monitor Completo**: Ejecuta ambos sistemas simultáneamente

## Administrar el Monitor en Segundo Plano

Para gestionar el monitor cuando se ejecuta en segundo plano, use PowerShell:

```powershell
# Iniciar el monitor en segundo plano
powershell -ExecutionPolicy Bypass -File "ejecutar_monitor_portable_background.ps1"

# Ver el estado del monitor
powershell -ExecutionPolicy Bypass -File "ejecutar_monitor_portable_background.ps1" -Status

# Detener el monitor
powershell -ExecutionPolicy Bypass -File "ejecutar_monitor_portable_background.ps1" -Stop
```

## Gestionar el Inicio Automático

Para administrar la configuración de inicio automático:

```powershell
# Ver el estado de la configuración de inicio automático
powershell -ExecutionPolicy Bypass -File "configurar_inicio_portable.ps1" -Status

# Eliminar del inicio automático
powershell -ExecutionPolicy Bypass -File "configurar_inicio_portable.ps1" -Remove

# Configurar nuevamente el inicio automático
powershell -ExecutionPolicy Bypass -File "configurar_inicio_portable.ps1"
```

## Verificación de Funcionamiento

Para verificar que el sistema está funcionando correctamente:

### Logs del Sistema

1. **Monitor de Sesión**: `logs/server_monitor.log`
2. **Monitor de Eventos**: `logs/windows_events.log`
3. **Sistema de Alertas**: `logs/alerts.log`

### Comandos de Estado

```powershell
# Ver estado del monitor
powershell -ExecutionPolicy Bypass -File "ejecutar_monitor_portable_background.ps1" -Status

# Probar el sistema de alertas
python-embedded\python.exe quadient_sender_simple.py test
```

### Verificación de Detección

El sistema detecta automáticamente:
- **Eventos críticos del sistema** (Event IDs configurables)
- **Procesos sospechosos** (nombres y ubicaciones)
- **Archivos maliciosos** (análisis de código y patrones)
- **Cambios en archivos críticos**

## Solución de Problemas

### El monitor no inicia

- Ejecute `INSTALAR_PORTABLE.bat` nuevamente para reparar la instalación
- Verifique que no haya una versión ya en ejecución

### No recibo notificaciones

- Verifique la configuración en `config.ini`
- Compruebe las credenciales de correo o API

### Error en la descarga de Python

- Si la descarga automática falla, descargue manualmente desde:
  [https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip](https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip)
- Coloque el archivo en una carpeta llamada `python-embedded` con el nombre `python-embed.zip`
- Vuelva a ejecutar `INSTALAR_PORTABLE.bat`

## Estructura de Archivos

Tras la instalación, la estructura de archivos será:

```plaintext
monitoreo_sesion/
├── python-embedded/        # Python portable para la ejecución
├── logs/                   # Carpeta de logs del monitor
├── config.ini              # Configuración del monitor
├── server_monitor.py       # Script principal
├── quadient_sender_simple.py # Módulo para notificaciones
├── INSTALAR_PORTABLE.bat   # Instalador portable
├── ejecutar_monitor_portable.bat # Ejecutar manualmente
└── ejecutar_monitor_portable_background.ps1 # Ejecutar en segundo plano
```

## Notas Importantes

- **No mueva** los archivos después de la instalación, ya que las rutas relativas son importantes
- Si necesita trasladar el monitor a otro equipo, copie toda la carpeta y ejecute nuevamente el instalador portable
- El monitor está diseñado para funcionar sin requerir permisos de administrador, pero algunas funciones pueden necesitarlos

## Configuración Avanzada

### Archivo de Configuración

El sistema se configura a través del archivo `config.ini` que incluye las siguientes secciones:

#### Monitoreo de Eventos (`[event_monitoring]`)
```ini
# Event IDs específicos a monitorear
event_ids = 1000,7034,7036,4625,4624
# Fuentes de eventos
sources = System,Application,Security
```

#### Monitoreo de Procesos (`[process_monitoring]`)
```ini
# Nombres de procesos sospechosos
suspicious_names = malware.exe,suspicious.exe,hack.exe
# Rutas sospechosas
suspicious_paths = temp,downloads,appdata\local\temp
```

#### Monitoreo de Archivos (`[file_monitoring]`)
```ini
# Directorios a monitorear
paths = C:\Windows\System32,C:\Users,C:\ProgramData
# Extensiones críticas
critical_extensions = .exe,.dll,.sys,.bat,.ps1
```

#### Sistema de Alertas (`[alerts]`)
```ini
# Método de alertas: email, webhook, notification, all
alert_method = all
# Configuración de email
smtp_server = smtp.gmail.com
email_username = tu_email@gmail.com
email_to = admin@empresa.com
```

### Personalización de Detección

- **Event IDs**: Modifique `event_ids` para monitorear eventos específicos
- **Procesos Maliciosos**: Agregue nombres a `suspicious_names`
- **Patrones de Código**: Configure `malicious_patterns` en la sección `[code_analysis]`
- **Umbrales de Alerta**: Ajuste valores en la sección `[thresholds]`
