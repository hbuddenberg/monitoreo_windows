@echo off
REM ===================================================================
REM INSTALADOR PORTABLE DEL MONITOR DE SESION
REM Este script configura el sistema completo sin necesitar Python preinstalado
REM ===================================================================

SETLOCAL EnableDelayedExpansion

REM Colores para mensajes
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

title Instalador Portable - Monitor de Sesion

echo %GREEN%=========================================================%RESET%
echo %GREEN%   INSTALADOR PORTABLE DEL MONITOR DE SESION V1.0%RESET%
echo %GREEN%=========================================================%RESET%
echo.
echo Este instalador configurara todo lo necesario sin requerir
echo una instalacion previa de Python en el sistema.
echo.

cd /d "%~dp0"

REM Verifica si ya existe la carpeta de python embebido
if exist "python-embedded\" (
    echo %YELLOW%Se detecto una instalacion previa de Python embebido%RESET%
    choice /C SN /M "Desea reinstalar Python embebido"
    if errorlevel 2 goto :SKIP_PYTHON_DOWNLOAD
)

echo %YELLOW%Descargando Python embebido (necesario para el monitor)...%RESET%
echo Esto puede tardar unos momentos...

REM Crear carpeta para Python embebido
if not exist "python-embedded\" mkdir "python-embedded"

REM Descargar Python embebido usando PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip' -OutFile 'python-embedded\python-embed.zip'}"

if not exist "python-embedded\python-embed.zip" (
    echo %RED%ERROR: No se pudo descargar Python embebido%RESET%
    echo Intentando metodo alternativo...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $client = New-Object System.Net.WebClient; $client.DownloadFile('https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip', 'python-embedded\python-embed.zip')}"
    
    if not exist "python-embedded\python-embed.zip" (
        echo %RED%ERROR: Ambos metodos de descarga fallaron.%RESET%
        echo Por favor, descargue manualmente Python embebido desde:
        echo https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip
        echo Y coloquelo en la carpeta 'python-embedded' con el nombre 'python-embed.zip'
        pause
        exit /b 1
    )
)

echo Descomprimiendo Python...
powershell -Command "& {Expand-Archive -Path 'python-embedded\python-embed.zip' -DestinationPath 'python-embedded' -Force}"

REM Descargar e instalar pip en Python embebido
echo Configurando pip en Python embebido...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'python-embedded\get-pip.py'}"
if not exist "python-embedded\get-pip.py" (
    echo %RED%ERROR: No se pudo descargar get-pip.py%RESET%
    pause
    exit /b 1
)

REM Configurar correctamente el archivo python310._pth
(
    echo python310.zip
    echo .
    echo.
    echo # Uncomment to run site.main^(^) automatically
    echo import site
) > "python-embedded\python310._pth"

REM Instalar pip
"python-embedded\python.exe" "python-embedded\get-pip.py"
if errorlevel 1 (
    echo %RED%ERROR: No se pudo instalar pip%RESET%
    pause
    exit /b 1
)

REM Instalar dependencias usando el pip de Python embebido
echo Instalando dependencias necesarias para el sistema de monitoreo...
echo Esto puede tardar varios minutos, especialmente pywin32...

REM Crear archivo de requirements si no existe
if not exist "requirements.txt" (
    echo Creando archivo de dependencias...
    (
        echo # Dependencias para el Sistema de Monitoreo de Eventos Windows
        echo.
        echo # Dependencias básicas del monitor
        echo requests^>=2.25.0
        echo configparser^>=5.0.0
        echo.
        echo # Dependencias para monitoreo de eventos Windows
        echo pywin32^>=227
        echo WMI^>=1.5.1
        echo watchdog^>=2.1.0
        echo.
        echo # Dependencias para análisis de código
        echo python-magic-bin^>=0.4.14
        echo.
        echo # Dependencias para notificaciones
        echo plyer^>=2.0
        echo win10toast^>=0.9
        echo.
        echo # Utilidades adicionales
        echo psutil^>=5.8.0
        echo colorama^>=0.4.4
    ) > requirements.txt
)

"python-embedded\python.exe" -m pip install --upgrade pip
"python-embedded\python.exe" -m pip install -r requirements.txt

if errorlevel 1 (
    echo %RED%ADVERTENCIA: Hubo problemas al instalar algunas dependencias%RESET%
    echo Intentando instalar dependencias críticas individualmente...
    
    REM Instalar dependencias críticas una por una
    echo Instalando pywin32...
    "python-embedded\python.exe" -m pip install pywin32
    
    echo Instalando WMI...
    "python-embedded\python.exe" -m pip install WMI
    
    echo Instalando watchdog...
    "python-embedded\python.exe" -m pip install watchdog
    
    echo Instalando requests...
    "python-embedded\python.exe" -m pip install requests
    
    echo Instalando plyer...
    "python-embedded\python.exe" -m pip install plyer
    
    echo %YELLOW%Instalación de dependencias completada con advertencias%RESET%
    echo Algunas funciones avanzadas pueden no estar disponibles.
)

:SKIP_PYTHON_DOWNLOAD

echo.
echo %GREEN%Python embebido configurado correctamente%RESET%
echo.

REM Desbloquear scripts PowerShell
echo Desbloqueando scripts PowerShell...
powershell -Command "Get-ChildItem -Path '%~dp0' -Filter '*.ps1' | Unblock-File"

REM Crear script actualizado para ejecutar el monitor
echo Configurando scripts de ejecucion...

REM Crear script de ejecución para el monitor con Python embebido
(
    echo @echo off
    echo REM Script para ejecutar el Sistema de Monitoreo de Eventos usando Python embebido
    echo.
    echo cd /d "%%~dp0"
    echo.
    echo echo ========================================================
    echo echo   SISTEMA DE MONITOREO DE EVENTOS WINDOWS
    echo echo ========================================================
    echo echo.
    echo echo Seleccione el tipo de monitoreo:
    echo echo 1. Monitor de Sesion (Original^)
    echo echo 2. Monitor de Eventos Windows (Nuevo^)
    echo echo 3. Monitor Completo (Ambos^)
    echo echo.
    echo set /p opcion="Ingrese su opcion (1-3): "
    echo.
    echo if "%%opcion%%"=="1" goto :SESSION_MONITOR
    echo if "%%opcion%%"=="2" goto :EVENTS_MONITOR  
    echo if "%%opcion%%"=="3" goto :FULL_MONITOR
    echo.
    echo echo Opcion invalida, iniciando monitor completo...
    echo goto :FULL_MONITOR
    echo.
    echo :SESSION_MONITOR
    echo echo Iniciando Monitor de Sesion...
    echo "python-embedded\python.exe" server_monitor.py
    echo goto :END
    echo.
    echo :EVENTS_MONITOR
    echo echo Iniciando Monitor de Eventos Windows...
    echo "python-embedded\python.exe" windows_event_monitor.py
    echo goto :END
    echo.
    echo :FULL_MONITOR
    echo echo Iniciando Sistema de Monitoreo Completo...
    echo echo Presione Ctrl+C para detener el monitoreo
    echo start /B "Monitor Sesion" "python-embedded\python.exe" server_monitor.py
    echo "python-embedded\python.exe" windows_event_monitor.py
    echo.
    echo :END
    echo if errorlevel 1 ^(
    echo     echo ERROR: No se pudo iniciar el monitor.
    echo     echo Verifique que todas las dependencias esten instaladas.
    echo     pause
    echo ^)
) > ejecutar_monitor_portable.bat

echo %GREEN%Script de ejecucion creado correctamente%RESET%

REM Crear versión portable del script de inicio en background
(
    echo # Script para ejecutar el monitor en segundo plano con Python embebido
    echo # No requiere permisos de administrador ni Python instalado en el sistema
    echo.
    echo param (
    echo     [string]$scriptPath = (Join-Path -Path $PSScriptRoot -ChildPath "server_monitor.py"^),
    echo     [switch]$Stop,
    echo     [switch]$Status
    echo )
    echo.
    echo $processName = "server_monitor"
    echo $pidFile = Join-Path -Path $PSScriptRoot -ChildPath "monitor.pid"
    echo $embeddedPython = Join-Path -Path $PSScriptRoot -ChildPath "python-embedded\python.exe"
    echo.
    echo function Show-Help {
    echo     Write-Host "=== GESTOR DEL MONITOR DE SESION (PORTABLE) ===" -ForegroundColor Green
    echo     Write-Host
    echo     Write-Host "Uso:"
    echo     Write-Host "  .\ejecutar_monitor_portable_background.ps1         # Iniciar monitor"
    echo     Write-Host "  .\ejecutar_monitor_portable_background.ps1 -Stop   # Detener monitor" 
    echo     Write-Host "  .\ejecutar_monitor_portable_background.ps1 -Status # Ver estado"
    echo     Write-Host
    echo }
    echo.
    echo function Start-Monitor {
    echo     # Verificar si ya está ejecutándose
    echo     if (Test-Path $pidFile) {
    echo         $pid = Get-Content $pidFile -ErrorAction SilentlyContinue
    echo         if ($pid -and (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
    echo             Write-Host "El monitor ya esta ejecutandose (PID: $pid)" -ForegroundColor Yellow
    echo             return
    echo         }
    echo     }
    echo     
    echo     # Verificar que Python embebido existe
    echo     if (-not (Test-Path $embeddedPython)) {
    echo         Write-Error "Python embebido no encontrado en: $embeddedPython"
    echo         Write-Host "Ejecute INSTALAR_PORTABLE.bat para configurar el entorno" -ForegroundColor Yellow
    echo         return
    echo     }
    echo     
    echo     # Verificar que el script existe
    echo     if (-not (Test-Path $scriptPath)) {
    echo         Write-Error "No se encuentra el script: $scriptPath"
    echo         return
    echo     }
    echo     
    echo     # Crear logs directory si no existe
    echo     $logsDir = Join-Path -Path $PSScriptRoot -ChildPath "logs"
    echo     if (-not (Test-Path $logsDir)) {
    echo         New-Item -Path $logsDir -ItemType Directory -Force | Out-Null
    echo     }
    echo     
    echo     Write-Host "Iniciando monitor en segundo plano usando Python embebido..." -ForegroundColor Green
    echo     
    echo     # Iniciar el proceso en segundo plano sin ventana usando Python embebido
    echo     $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    echo     $startInfo.FileName = $embeddedPython
    echo     $startInfo.Arguments = "`"$scriptPath`""
    echo     $startInfo.WorkingDirectory = $PSScriptRoot
    echo     $startInfo.UseShellExecute = $false
    echo     $startInfo.CreateNoWindow = $true
    echo     
    echo     $process = New-Object System.Diagnostics.Process
    echo     $process.StartInfo = $startInfo
    echo     $process.Start() | Out-Null
    echo     
    echo     # Guardar el PID del proceso
    echo     $process.Id | Out-File -FilePath $pidFile -Force
    echo     
    echo     Write-Host "Monitor iniciado en segundo plano (PID: $($process.Id))" -ForegroundColor Green
    echo     Write-Host "Los logs se guardan en: $logsDir\server_monitor.log" -ForegroundColor Cyan
    echo }
    echo.
    echo function Stop-Monitor {
    echo     if (-not (Test-Path $pidFile)) {
    echo         Write-Host "Monitor no está ejecutándose (no se encontró PID)" -ForegroundColor Yellow
    echo         return
    echo     }
    echo     
    echo     $pid = Get-Content $pidFile -ErrorAction SilentlyContinue
    echo     if (-not $pid) {
    echo         Write-Host "Archivo PID vacío o dañado" -ForegroundColor Yellow
    echo         Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    echo         return
    echo     }
    echo     
    echo     try {
    echo         $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
    echo         if ($process) {
    echo             $process | Stop-Process -Force
    echo             Write-Host "Monitor detenido (PID: $pid)" -ForegroundColor Green
    echo         } else {
    echo             Write-Host "Proceso no encontrado (PID: $pid)" -ForegroundColor Yellow
    echo         }
    echo     } catch {
    echo         Write-Host "Error al detener el proceso: $_" -ForegroundColor Red
    echo     }
    echo     
    echo     # Eliminar archivo PID
    echo     Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    echo }
    echo.
    echo function Get-MonitorStatus {
    echo     if (-not (Test-Path $pidFile)) {
    echo         Write-Host "Estado: NO EJECUTÁNDOSE" -ForegroundColor Red
    echo         return
    echo     }
    echo     
    echo     $pid = Get-Content $pidFile -ErrorAction SilentlyContinue
    echo     if (-not $pid) {
    echo         Write-Host "Estado: DESCONOCIDO (archivo PID vacío)" -ForegroundColor Yellow
    echo         return
    echo     }
    echo     
    echo     $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
    echo     if ($process) {
    echo         Write-Host "Estado: EJECUTÁNDOSE (PID: $pid)" -ForegroundColor Green
    echo         $uptime = (Get-Date) - $process.StartTime
    echo         Write-Host "Tiempo de ejecución: $($uptime.Days) días, $($uptime.Hours) horas, $($uptime.Minutes) minutos"
    echo         
    echo         # Mostrar ruta de logs
    echo         $logsDir = Join-Path -Path $PSScriptRoot -ChildPath "logs"
    echo         $logFile = Join-Path -Path $logsDir -ChildPath "server_monitor.log"
    echo         if (Test-Path $logFile) {
    echo             Write-Host "Archivo de log: $logFile" -ForegroundColor Cyan
    echo             
    echo             # Mostrar últimas líneas del log
    echo             Write-Host "Últimas entradas del log:" -ForegroundColor Cyan
    echo             Get-Content $logFile -Tail 5 | ForEach-Object { Write-Host "  $_" }
    echo         }
    echo     } else {
    echo         Write-Host "Estado: NO EJECUTÁNDOSE (PID: $pid no encontrado)" -ForegroundColor Red
    echo         Write-Host "Eliminando archivo PID obsoleto..."
    echo         Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    echo     }
    echo }
    echo.
    echo # Lógica principal
    echo if ($PSVersionTable.PSVersion.Major -lt 3) {
    echo     Write-Error "Este script requiere PowerShell 3.0 o superior"
    echo     exit 1
    echo }
    echo.
    echo if ($Stop) {
    echo     Stop-Monitor
    echo } elseif ($Status) {
    echo     Get-MonitorStatus
    echo } else {
    echo     Start-Monitor
    echo }
) > ejecutar_monitor_portable_background.ps1

echo %GREEN%Script de ejecucion en segundo plano creado correctamente%RESET%

REM Crear un script de configuración de inicio automático usando Python embebido
(
    echo # Script para configurar inicio automático con Python embebido
    echo # No requiere Python instalado en el sistema
    echo.
    echo param (
    echo     [switch]$Remove,
    echo     [switch]$Status
    echo )
    echo.
    echo $startupFolder = [Environment]::GetFolderPath("Startup"^)
    echo $shortcutPath = Join-Path -Path $startupFolder -ChildPath "Monitor Sesion Servidor (Portable).lnk"
    echo $scriptDir = $PSScriptRoot
    echo $backgroundScript = Join-Path -Path $scriptDir -ChildPath "ejecutar_monitor_portable_background.ps1"
    echo.
    echo if ($Remove) {
    echo     # Eliminar del inicio
    echo     if (Test-Path $shortcutPath) {
    echo         Remove-Item $shortcutPath -Force
    echo         Write-Host "Monitor eliminado del inicio automatico" -ForegroundColor Green
    echo     } else {
    echo         Write-Host "No hay acceso directo configurado" -ForegroundColor Yellow
    echo     }
    echo }
    echo elseif ($Status) {
    echo     # Mostrar estado
    echo     Write-Host "=== ESTADO DEL INICIO AUTOMATICO ===" -ForegroundColor Cyan
    echo     Write-Host "Carpeta de inicio: $startupFolder"
    echo     
    echo     if (Test-Path $shortcutPath) {
    echo         Write-Host "Estado: CONFIGURADO" -ForegroundColor Green
    echo     } else {
    echo         Write-Host "Estado: NO CONFIGURADO" -ForegroundColor Red
    echo     }
    echo }
    echo else {
    echo     # Agregar al inicio
    echo     Write-Host "Configurando inicio automatico del monitor..." -ForegroundColor Green
    echo     
    echo     # Verificar que el script background existe
    echo     if (-not (Test-Path $backgroundScript)) {
    echo         Write-Error "No se encuentra el script: $backgroundScript"
    echo         exit 1
    echo     }
    echo     
    echo     # Verificar Python embebido
    echo     $embeddedPython = Join-Path -Path $scriptDir -ChildPath "python-embedded\python.exe"
    echo     if (-not (Test-Path $embeddedPython)) {
    echo         Write-Error "Python embebido no encontrado. Ejecute INSTALAR_PORTABLE.bat primero."
    echo         exit 1
    echo     }
    echo     
    echo     try {
    echo         # Crear acceso directo
    echo         $WScriptShell = New-Object -ComObject WScript.Shell
    echo         $shortcut = $WScriptShell.CreateShortcut($shortcutPath)
    echo         $shortcut.TargetPath = "powershell.exe"
    echo         $shortcut.Arguments = "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$backgroundScript`""
    echo         $shortcut.WorkingDirectory = $scriptDir
    echo         $shortcut.Description = "Monitor de Sesion de Servidor (Portable)"
    echo         $shortcut.Save()
    echo         
    echo         Write-Host "Configuracion completada exitosamente" -ForegroundColor Green
    echo         Write-Host "El monitor se ejecutara automaticamente al iniciar Windows" -ForegroundColor Yellow
    echo         
    echo         # Preguntar si quiere iniciarlo ahora
    echo         $respuesta = Read-Host "Iniciar el monitor ahora? (s/n)"
    echo         if ($respuesta -match "^[sS]") {
    echo             & $backgroundScript
    echo         }
    echo         
    echo     } catch {
    echo         Write-Error "Error al crear acceso directo: $_"
    echo         exit 1
    echo     }
    echo }
) > configurar_inicio_portable.ps1

REM Configurar inicio automático
echo.
echo %YELLOW%Configurando inicio automatico del monitor...%RESET%
powershell -ExecutionPolicy Bypass -File "%~dp0configurar_inicio_portable.ps1"

echo.
echo %GREEN%=====================================================%RESET%
echo %GREEN%  INSTALACION PORTABLE COMPLETADA EXITOSAMENTE%RESET%
echo %GREEN%=====================================================%RESET%
echo.
echo El monitor ahora puede ejecutarse sin necesidad de tener Python
echo instalado en el sistema. Los archivos necesarios para ejecutar
echo el monitor son:
echo.
echo %YELLOW%- Python embebido (carpeta python-embedded)%RESET%
echo %YELLOW%- server_monitor.py y archivos relacionados%RESET%
echo %YELLOW%- ejecutar_monitor_portable.bat (para ejecucion manual)%RESET%
echo.
echo Para probar el sistema, puede ejecutar:
echo %YELLOW%  ejecutar_monitor_portable.bat%RESET%
echo.
echo Para mas opciones, ejecute:
echo %YELLOW%  powershell -ExecutionPolicy Bypass -File "ejecutar_monitor_portable_background.ps1" -Status%RESET%
echo.
pause
