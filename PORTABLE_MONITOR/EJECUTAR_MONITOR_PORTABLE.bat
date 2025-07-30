@echo off
REM ===================================================================
REM LAUNCHER DEL MONITOR PORTABLE COMPLETO DE EVENTOS WINDOWS
REM Version mejorada con deteccion de eventos de reinicio/apagado
REM ===================================================================

SETLOCAL EnableDelayedExpansion

REM Colores para mensajes
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

title Monitor Portable Completo de Eventos Windows

echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo %GREEN%   MONITOR PORTABLE COMPLETO DE EVENTOS WINDOWS%RESET%
echo %GREEN%   Version sin permisos administrativos - MEJORADO%RESET%
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo.
echo %BLUE%🚀 Funcionalidades Incluidas:%RESET%
echo   %YELLOW%✅ Deteccion de eventos de reinicio/apagado%RESET%
echo   %YELLOW%✅ Busqueda especifica de Event IDs%RESET%
echo   %YELLOW%✅ Monitoreo de procesos sospechosos%RESET%
echo   %YELLOW%✅ Monitoreo de archivos criticos%RESET%
echo   %YELLOW%✅ Sistema de alertas avanzado%RESET%
echo   %YELLOW%✅ Notificaciones multiples (Email, Webhook, Windows)%RESET%
echo.

cd /d "%~dp0"

REM Verificar que Python embebido exista
if not exist "python-embedded\python.exe" (
    echo %RED%ERROR: Python embebido no encontrado%RESET%
    echo.
    echo %YELLOW%Posibles soluciones:%RESET%
    echo 1. Ejecute INSTALAR_PORTABLE.bat en el directorio principal
    echo 2. Ejecute REPARAR_PYTHON_EMBEBIDO.bat si ya instalo
    echo 3. Use CREAR_MONITOR_SIMPLE.bat como alternativa
    echo.
    pause
    exit /b 1
)

REM Verificar Python embebido
echo %YELLOW%Verificando Python embebido...%RESET%
"python-embedded\python.exe" --version
if errorlevel 1 (
    echo %RED%ERROR: Python embebido no funciona correctamente%RESET%
    echo Ejecute REPARAR_PYTHON_EMBEBIDO.bat
    pause
    exit /b 1
)

echo %GREEN%✓ Python embebido funcionando correctamente%RESET%
echo.

REM Verificar archivo de configuracion
if not exist "config.ini" (
    echo %YELLOW%Advertencia: config.ini no encontrado, usando configuracion por defecto%RESET%
    echo.
)

REM Verificar dependencias criticas
echo %YELLOW%Verificando dependencias...%RESET%
"python-embedded\python.exe" -c "import psutil; print('✓ psutil disponible')" 2>nul
if errorlevel 1 (
    echo %YELLOW%⚠️ psutil no disponible - usando metodos alternativos%RESET%
) else (
    echo %GREEN%✓ psutil disponible%RESET%
)

"python-embedded\python.exe" -c "import watchdog; print('✓ watchdog disponible')" 2>nul
if errorlevel 1 (
    echo %YELLOW%⚠️ watchdog no disponible - monitoreo de archivos limitado%RESET%
) else (
    echo %GREEN%✓ watchdog disponible%RESET%
)

echo.

REM Crear directorio de logs si no existe
if not exist "logs" mkdir "logs"

REM Mostrar configuracion actual
echo %BLUE%📋 Configuracion Actual:%RESET%
echo %YELLOW%Event IDs especificos: 1074,6008,41 (eventos de reinicio/apagado)%RESET%
echo %YELLOW%Directorios monitoreados: Desktop, Downloads, Documents, Temp%RESET%
echo %YELLOW%Sistema de alertas: Activado (multiples canales)%RESET%
echo.

REM Preguntar si quiere configurar email/webhook
set /p setup_alerts="¿Configurar alertas por email/webhook ahora? (s/N): "
if /i "%setup_alerts%"=="s" (
    echo.
    echo %BLUE%Configuracion Rapida de Alertas:%RESET%
    echo.
    set /p email_user="Email para alertas (Enter para omitir): "
    if not "!email_user!"=="" (
        set /p email_pass="Password del email: "
        set /p email_to="Email destino: "
        
        REM Actualizar config.ini basico
        if not "!email_pass!"=="" if not "!email_to!"=="" (
            echo email_username = !email_user! >> config_temp.ini
            echo email_password = !email_pass! >> config_temp.ini  
            echo email_to = !email_to! >> config_temp.ini
            echo %GREEN%✓ Configuracion de email guardada temporalmente%RESET%
        )
    )
    
    set /p webhook_url="URL de webhook (Slack/Discord, Enter para omitir): "
    if not "!webhook_url!"=="" (
        echo webhook_url = !webhook_url! >> config_temp.ini
        echo %GREEN%✓ Webhook configurado%RESET%
    )
    echo.
)

echo %GREEN%🚀 Iniciando Monitor Portable Completo...%RESET%
echo.
echo %YELLOW%📊 El monitor incluye:%RESET%
echo   • Deteccion automatica de eventos de reinicio
echo   • Busqueda de Event IDs especificos (1074, 6008, 41)  
echo   • Monitoreo de procesos maliciosos
echo   • Analisis de archivos sospechosos
echo   • Alertas por multiple canales
echo.
echo %YELLOW%📁 Logs en: logs\portable_monitor.log%RESET%
echo %RED%⚠️  Presione Ctrl+C para detener el monitor%RESET%
echo.
echo %GREEN%════════════════════════════════════════════════════════════════%RESET%
echo.

REM Ejecutar el monitor
"python-embedded\python.exe" portable_monitor.py

REM Verificar como termino
set exit_code=%errorlevel%

echo.
echo %GREEN%════════════════════════════════════════════════════════════════%RESET%

if %exit_code% equ 0 (
    echo %GREEN%✓ Monitor detenido correctamente%RESET%
) else (
    echo %RED%✗ Monitor termino con errores (codigo: %exit_code%)%RESET%
    echo.
    echo %YELLOW%Posibles causas:%RESET%
    echo 1. Dependencias faltantes
    echo 2. Permisos insuficientes
    echo 3. Configuracion incorrecta
    echo.
    echo %YELLOW%Revise el archivo: logs\portable_monitor.log%RESET%
    echo.
)

REM Limpiar archivos temporales
if exist "config_temp.ini" del "config_temp.ini"

echo.
echo %BLUE%Presione cualquier tecla para salir...%RESET%
pause >nul
