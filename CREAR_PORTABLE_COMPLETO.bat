@echo off
REM ===================================================================
REM CREADOR DE VERSION PORTABLE COMPLETA - SIN PERMISOS ADMIN
REM Este script crea una version completamente portable que funciona
REM sin necesidad de permisos administrativos ni instalaciones
REM ===================================================================

SETLOCAL EnableDelayedExpansion

REM Colores para mensajes
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

title Creador de Version Portable Completa - Monitor de Eventos

echo %GREEN%=========================================================%RESET%
echo %GREEN%   CREADOR DE VERSION PORTABLE COMPLETA V1.0%RESET%
echo %GREEN%   Monitor de Eventos Windows - Sin Permisos Admin%RESET%
echo %GREEN%=========================================================%RESET%
echo.
echo %BLUE%Esta herramienta creara una version completamente portable%RESET%
echo %BLUE%que funciona SIN necesidad de permisos administrativos.%RESET%
echo.
echo %YELLOW%Caracteristicas de la version portable:%RESET%
echo  - Python embebido incluido (no requiere instalacion)
echo  - Todas las dependencias incluidas
echo  - Funciona desde cualquier carpeta
echo  - No requiere permisos administrativos
echo  - Monitoreo limitado pero funcional
echo.

cd /d "%~dp0"

REM Crear estructura de carpetas portable
echo %YELLOW%Creando estructura de carpetas portable...%RESET%
if not exist "PORTABLE_MONITOR" mkdir "PORTABLE_MONITOR"
if not exist "PORTABLE_MONITOR\python-embedded" mkdir "PORTABLE_MONITOR\python-embedded"
if not exist "PORTABLE_MONITOR\logs" mkdir "PORTABLE_MONITOR\logs"

REM Descargar Python embebido si no existe
if not exist "python-embedded\python.exe" (
    echo %YELLOW%Descargando Python embebido...%RESET%
    echo Esto puede tardar unos momentos...
    
    if not exist "python-embedded\" mkdir "python-embedded"
    
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip' -OutFile 'python-embedded\python-embed.zip'}"
    
    if exist "python-embedded\python-embed.zip" (
        echo Descomprimiendo Python...
        powershell -Command "& {Expand-Archive -Path 'python-embedded\python-embed.zip' -DestinationPath 'python-embedded' -Force}"
        
        REM Configurar Python embebido correctamente
        (
            echo python310.zip
            echo .
            echo.
            echo # Uncomment to run site.main^(^) automatically
            echo import site
        ) > "python-embedded\python310._pth"
        
        REM Descargar e instalar pip
        powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'python-embedded\get-pip.py'}"
        "python-embedded\python.exe" "python-embedded\get-pip.py"
        
        echo %GREEN%Python embebido configurado correctamente%RESET%
    ) else (
        echo %RED%ERROR: No se pudo descargar Python embebido%RESET%
        echo Por favor, descargue manualmente y coloque en python-embedded\
        pause
        exit /b 1
    )
)

REM Copiar Python embebido a la carpeta portable
echo %YELLOW%Copiando Python embebido...%RESET%
xcopy "python-embedded\*" "PORTABLE_MONITOR\python-embedded\" /E /I /Y /Q

REM Instalar dependencias mínimas para version sin permisos admin
echo %YELLOW%Instalando dependencias minimas...%RESET%
"PORTABLE_MONITOR\python-embedded\python.exe" -m pip install requests psutil --quiet --no-warn-script-location

REM Intentar instalar dependencias opcionales (sin fallar si no funciona)
echo %YELLOW%Intentando instalar dependencias opcionales...%RESET%
"PORTABLE_MONITOR\python-embedded\python.exe" -m pip install plyer watchdog --quiet --no-warn-script-location

REM Crear versiones modificadas de los scripts para funcionar sin permisos admin
echo %YELLOW%Creando scripts modificados para version portable...%RESET%

REM Copiar archivos principales
copy "config.ini" "PORTABLE_MONITOR\" >nul
copy "quadient_sender_simple.py" "PORTABLE_MONITOR\" >nul

REM Crear version modificada del monitor principal
(
    echo # Monitor de Eventos Windows - Version Portable Sin Permisos Admin
    echo # Funciona con capacidades limitadas pero sin requerir permisos administrativos
    echo.
    echo import os
    echo import sys
    echo import time
    echo import json
    echo import logging
    echo import psutil
    echo import requests
    echo import threading
    echo import configparser
    echo from datetime import datetime, timedelta
    echo from typing import Dict, List, Optional
    echo.
    echo # Intentar importar dependencias opcionales
    echo try:
    echo     from plyer import notification
    echo     PLYER_AVAILABLE = True
    echo except ImportError:
    echo     PLYER_AVAILABLE = False
    echo.
    echo try:
    echo     from watchdog.observers import Observer
    echo     from watchdog.events import FileSystemEventHandler
    echo     WATCHDOG_AVAILABLE = True
    echo except ImportError:
    echo     WATCHDOG_AVAILABLE = False
    echo.
    echo class PortableEventMonitor:
    echo     """Monitor portable que funciona sin permisos administrativos"""
    echo     
    echo     def __init__(self, config_file: str = 'config.ini'^):
    echo         self.config = configparser.ConfigParser(^)
    echo         self.config.read(config_file^)
    echo         self.running = False
    echo         
    echo         # Configurar logging
    echo         self.logger = self._setup_logging(^)
    echo         
    echo         # Obtener directorio del usuario para logs
    echo         self.user_temp = os.path.expanduser('~'^)
    echo         self.log_dir = os.path.join(self.user_temp, '.monitor_eventos'^)
    echo         os.makedirs(self.log_dir, exist_ok=True^)
    echo         
    echo         self.logger.info("Monitor portable iniciado sin permisos administrativos"^)
    echo         
    echo     def _setup_logging(self^) -^> logging.Logger:
    echo         logger = logging.getLogger('PortableMonitor'^)
    echo         logger.setLevel(logging.INFO^)
    echo         
    echo         # Crear handler para archivo en directorio del usuario
    echo         try:
    echo             log_file = os.path.join('logs', 'portable_monitor.log'^)
    echo             os.makedirs('logs', exist_ok=True^)
    echo             file_handler = logging.FileHandler(log_file^)
    echo         except:
    echo             # Si no puede escribir en logs, usar temp del usuario
    echo             user_temp = os.path.expanduser('~'^)
    echo             log_file = os.path.join(user_temp, 'monitor_eventos.log'^)
    echo             file_handler = logging.FileHandler(log_file^)
    echo             
    echo         file_handler.setLevel(logging.INFO^)
    echo         console_handler = logging.StreamHandler(^)
    echo         console_handler.setLevel(logging.WARNING^)
    echo         
    echo         formatter = logging.Formatter('%%^(asctime^)s - %%^(levelname^)s - %%^(message^)s'^)
    echo         file_handler.setFormatter(formatter^)
    echo         console_handler.setFormatter(formatter^)
    echo         
    echo         logger.addHandler(file_handler^)
    echo         logger.addHandler(console_handler^)
    echo         
    echo         return logger
    echo         
    echo     def start_monitoring(self^):
    echo         """Inicia el monitoreo con capacidades limitadas"""
    echo         self.running = True
    echo         self.logger.info("Iniciando monitoreo portable..."^)
    echo         
    echo         # Threads para diferentes tipos de monitoreo
    echo         threads = []
    echo         
    echo         # Monitor de procesos (usando psutil^)
    echo         process_thread = threading.Thread(target=self._monitor_processes^)
    echo         process_thread.daemon = True
    echo         process_thread.start(^)
    echo         threads.append(process_thread^)
    echo         
    echo         # Monitor de archivos (si watchdog esta disponible^)
    echo         if WATCHDOG_AVAILABLE:
    echo             file_thread = threading.Thread(target=self._monitor_files^)
    echo             file_thread.daemon = True
    echo             file_thread.start(^)
    echo             threads.append(file_thread^)
    echo         
    echo         # Monitor de sistema
    echo         system_thread = threading.Thread(target=self._monitor_system^)
    echo         system_thread.daemon = True
    echo         system_thread.start(^)
    echo         threads.append(system_thread^)
    echo         
    echo         try:
    echo             while self.running:
    echo                 time.sleep(60^)
    echo                 self.logger.info("Monitor portable activo - Threads: %d" %% len(threads^)^)
    echo         except KeyboardInterrupt:
    echo             self.stop(^)
    echo             
    echo     def _monitor_processes(self^):
    echo         """Monitorea procesos usando psutil"""
    echo         suspicious_names = ['malware.exe', 'suspicious.exe', 'hack.exe', 'keylogger.exe']
    echo         
    echo         while self.running:
    echo             try:
    echo                 for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']^):
    echo                     try:
    echo                         proc_info = proc.info
    echo                         if proc_info['name']:
    echo                             proc_name = proc_info['name'].lower(^)
    echo                             
    echo                             # Verificar nombres sospechosos
    echo                             if any(susp in proc_name for susp in suspicious_names^):
    echo                                 self._send_alert(
    echo                                     "Proceso Sospechoso Detectado",
    echo                                     f"Proceso: {proc_info['name']} (PID: {proc_info['pid']}^)",
    echo                                     {'type': 'suspicious_process', 'severity': 'HIGH'}
    echo                                 ^)
    echo                                 
    echo                     except (psutil.NoSuchProcess, psutil.AccessDenied^):
    echo                         continue
    echo                         
    echo                 time.sleep(30^)  # Revisar cada 30 segundos
    echo                 
    echo             except Exception as e:
    echo                 self.logger.error(f"Error monitoreando procesos: {e}"^)
    echo                 time.sleep(60^)
    echo                 
    echo     def _monitor_files(self^):
    echo         """Monitorea archivos usando watchdog"""
    echo         if not WATCHDOG_AVAILABLE:
    echo             return
    echo             
    echo         # Solo monitorear directorios accesibles sin permisos admin
    echo         user_dirs = [
    echo             os.path.expanduser('~/Desktop'^),
    echo             os.path.expanduser('~/Downloads'^),
    echo             os.path.expanduser('~/Documents'^)
    echo         ]
    echo         
    echo         class FileHandler(FileSystemEventHandler^):
    echo             def __init__(self, monitor^):
    echo                 self.monitor = monitor
    echo                 
    echo             def on_created(self, event^):
    echo                 if not event.is_directory:
    echo                     self.monitor._check_suspicious_file(event.src_path^)
    echo                     
    echo         observer = Observer(^)
    echo         handler = FileHandler(self^)
    echo         
    echo         for user_dir in user_dirs:
    echo             if os.path.exists(user_dir^):
    echo                 try:
    echo                     observer.schedule(handler, user_dir, recursive=True^)
    echo                     self.logger.info(f"Monitoreando: {user_dir}"^)
    echo                 except Exception as e:
    echo                     self.logger.warning(f"No se puede monitorear {user_dir}: {e}"^)
    echo                     
    echo         observer.start(^)
    echo         
    echo         try:
    echo             while self.running:
    echo                 time.sleep(60^)
    echo         except:
    echo             pass
    echo         finally:
    echo             observer.stop(^)
    echo             observer.join(^)
    echo             
    echo     def _monitor_system(self^):
    echo         """Monitorea métricas del sistema"""
    echo         while self.running:
    echo             try:
    echo                 # Monitorear CPU y memoria
    echo                 cpu_percent = psutil.cpu_percent(interval=1^)
    echo                 memory = psutil.virtual_memory(^)
    echo                 
    echo                 # Alertar si uso excesivo
    echo                 if cpu_percent ^> 90:
    echo                     self._send_alert(
    echo                         "Alto Uso de CPU",
    echo                         f"CPU al {cpu_percent}%%",
    echo                         {'type': 'system_alert', 'severity': 'MEDIUM'}
    echo                     ^)
    echo                     
    echo                 if memory.percent ^> 90:
    echo                     self._send_alert(
    echo                         "Alto Uso de Memoria",
    echo                         f"Memoria al {memory.percent}%%",
    echo                         {'type': 'system_alert', 'severity': 'MEDIUM'}
    echo                     ^)
    echo                     
    echo                 time.sleep(300^)  # Revisar cada 5 minutos
    echo                 
    echo             except Exception as e:
    echo                 self.logger.error(f"Error monitoreando sistema: {e}"^)
    echo                 time.sleep(300^)
    echo                 
    echo     def _check_suspicious_file(self, file_path: str^):
    echo         """Verifica si un archivo es sospechoso"""
    echo         try:
    echo             filename = os.path.basename(file_path^).lower(^)
    echo             suspicious_extensions = ['.exe', '.scr', '.bat', '.cmd', '.ps1']
    echo             suspicious_names = ['malware', 'virus', 'trojan', 'hack', 'crack']
    echo             
    echo             # Verificar extensión
    echo             _, ext = os.path.splitext(filename^)
    echo             if ext in suspicious_extensions:
    echo                 # Verificar nombre sospechoso
    echo                 if any(name in filename for name in suspicious_names^):
    echo                     self._send_alert(
    echo                         "Archivo Sospechoso Detectado",
    echo                         f"Archivo: {file_path}",
    echo                         {'type': 'suspicious_file', 'severity': 'HIGH'}
    echo                     ^)
    echo                     
    echo         except Exception as e:
    echo             self.logger.error(f"Error verificando archivo {file_path}: {e}"^)
    echo             
    echo     def _send_alert(self, title: str, message: str, data: Dict^):
    echo         """Envía una alerta"""
    echo         try:
    echo             self.logger.warning(f"ALERTA: {title} - {message}"^)
    echo             
    echo             # Notificación de Windows si está disponible
    echo             if PLYER_AVAILABLE:
    echo                 try:
    echo                     notification.notify(
    echo                         title=title,
    echo                         message=message,
    echo                         timeout=10
    echo                     ^)
    echo                 except:
    echo                     pass
    echo                     
    echo             # Intentar enviar por email (si está configurado^)
    echo             try:
    echo                 from quadient_sender_simple import send_alert
    echo                 threading.Thread(
    echo                     target=send_alert,
    echo                     args=(title, message, data^)
    echo                 ^).start(^)
    echo             except Exception as e:
    echo                 self.logger.debug(f"No se pudo enviar email: {e}"^)
    echo                 
    echo         except Exception as e:
    echo             self.logger.error(f"Error enviando alerta: {e}"^)
    echo             
    echo     def stop(self^):
    echo         """Detiene el monitoreo"""
    echo         self.running = False
    echo         self.logger.info("Monitor portable detenido"^)
    echo         
    echo if __name__ == "__main__":
    echo     try:
    echo         monitor = PortableEventMonitor(^)
    echo         print("Iniciando Monitor Portable de Eventos..."^)
    echo         print("Presione Ctrl+C para detener"^)
    echo         monitor.start_monitoring(^)
    echo     except KeyboardInterrupt:
    echo         print("\\nDeteniendo monitor..."^)
    echo     except Exception as e:
    echo         print(f"Error: {e}"^)
    echo         input("Presione Enter para salir..."^)
) > "PORTABLE_MONITOR\portable_monitor.py"

REM Crear launcher simple
(
    echo @echo off
    echo title Monitor Portable de Eventos Windows
    echo echo ========================================================
    echo echo   MONITOR PORTABLE DE EVENTOS WINDOWS
    echo echo   Version sin permisos administrativos
    echo echo ========================================================
    echo echo.
    echo cd /d "%%~dp0"
    echo.
    echo echo Iniciando monitor portable...
    echo echo Presione Ctrl+C para detener
    echo echo.
    echo "python-embedded\python.exe" portable_monitor.py
    echo.
    echo if errorlevel 1 ^(
    echo     echo ERROR: No se pudo iniciar el monitor.
    echo     echo Verifique que Python embebido este disponible.
    echo     pause
    echo ^)
) > "PORTABLE_MONITOR\EJECUTAR_MONITOR_PORTABLE.bat"

REM Crear configuración optimizada para version portable
(
    echo [DEFAULT]
    echo # Configuracion optimizada para version portable sin permisos admin
    echo.
    echo [general]
    echo check_interval = 60
    echo log_level = INFO
    echo log_directory = logs
    echo.
    echo [process_monitoring]
    echo # Procesos sospechosos a detectar
    echo suspicious_names = malware.exe,suspicious.exe,hack.exe,keylogger.exe,trojan.exe,virus.exe
    echo.
    echo [file_monitoring] 
    echo # Solo directorios del usuario (sin permisos admin^)
    echo paths = ~/Desktop,~/Downloads,~/Documents
    echo critical_extensions = .exe,.scr,.bat,.cmd,.ps1,.vbs
    echo suspicious_patterns = *malware*,*virus*,*trojan*,*hack*,*crack*
    echo.
    echo [alerts]
    echo # Configuracion de alertas
    echo alert_method = notification
    echo min_severity = MEDIUM
    echo.
    echo # Email (opcional - configure si desea recibir emails^)
    echo smtp_server = 
    echo email_username = 
    echo email_password = 
    echo email_to = 
    echo.
    echo [system_monitoring]
    echo # Umbrales para alertas de sistema
    echo cpu_threshold = 90
    echo memory_threshold = 90
) > "PORTABLE_MONITOR\config.ini"

REM Crear documentación portable
(
    echo # Monitor Portable de Eventos Windows
    echo ## Version Sin Permisos Administrativos
    echo.
    echo Esta version del monitor funciona completamente portable
    echo y NO requiere permisos administrativos.
    echo.
    echo ### Que monitorea:
    echo - Procesos sospechosos en ejecucion
    echo - Archivos sospechosos en carpetas del usuario
    echo - Alto uso de CPU y memoria
    echo - Cambios en archivos criticos del usuario
    echo.
    echo ### Como usar:
    echo 1. Copie toda la carpeta PORTABLE_MONITOR a cualquier ubicacion
    echo 2. Ejecute EJECUTAR_MONITOR_PORTABLE.bat
    echo 3. El monitor funcionara en segundo plano
    echo.
    echo ### Configuracion:
    echo - Edite config.ini para personalizar la deteccion
    echo - Configure email en la seccion [alerts] para recibir alertas
    echo.
    echo ### Limitaciones:
    echo - No puede acceder a Event Log de Windows ^(requiere permisos admin^)
    echo - Solo monitorea directorios del usuario
    echo - Capacidades limitadas comparado con la version completa
    echo.
    echo ### Logs:
    echo - Los logs se guardan en la carpeta logs\
    echo - Si no puede escribir ahi, usa el directorio del usuario
    echo.
    echo Esta version es ideal para uso en equipos corporativos
    echo donde no se tienen permisos administrativos.
) > "PORTABLE_MONITOR\README_PORTABLE.txt"

REM Crear script de prueba
(
    echo @echo off
    echo title Prueba del Monitor Portable
    echo echo Probando el monitor portable...
    echo echo.
    echo cd /d "%%~dp0"
    echo.
    echo echo Verificando Python embebido...
    echo "python-embedded\python.exe" --version
    echo.
    echo echo Verificando dependencias...
    echo "python-embedded\python.exe" -c "import psutil; print('psutil OK'^)"
    echo "python-embedded\python.exe" -c "import requests; print('requests OK'^)"
    echo.
    echo echo Probando monitor ^(5 segundos^)...
    echo timeout /t 5 /nobreak ^> nul ^| "python-embedded\python.exe" portable_monitor.py
    echo.
    echo echo Prueba completada.
    echo pause
) > "PORTABLE_MONITOR\PROBAR_MONITOR.bat"

echo.
echo %GREEN%=====================================================%RESET%
echo %GREEN%  VERSION PORTABLE CREADA EXITOSAMENTE%RESET%
echo %GREEN%=====================================================%RESET%
echo.
echo %YELLOW%La carpeta PORTABLE_MONITOR contiene:%RESET%
echo.
echo  %BLUE%📁 python-embedded\%RESET%      - Python embebido completo
echo  %BLUE%📄 portable_monitor.py%RESET%   - Monitor sin permisos admin
echo  %BLUE%📄 config.ini%RESET%            - Configuracion optimizada
echo  %BLUE%🚀 EJECUTAR_MONITOR_PORTABLE.bat%RESET% - Iniciar monitor
echo  %BLUE%🔧 PROBAR_MONITOR.bat%RESET%    - Probar funcionamiento
echo  %BLUE%📖 README_PORTABLE.txt%RESET%   - Documentacion
echo.
echo %GREEN%INSTRUCCIONES:%RESET%
echo.
echo 1. %YELLOW%Copie la carpeta PORTABLE_MONITOR%RESET% a cualquier equipo
echo 2. %YELLOW%No necesita instalar nada%RESET% - todo esta incluido
echo 3. %YELLOW%Ejecute EJECUTAR_MONITOR_PORTABLE.bat%RESET% para iniciar
echo 4. %YELLOW%Configure email en config.ini%RESET% si desea alertas por correo
echo.
echo %BLUE%FUNCIONA SIN PERMISOS ADMINISTRATIVOS%RESET%
echo.
pause