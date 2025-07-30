@echo off
REM ===================================================================
REM CREADOR DE MONITOR SIMPLE - Sin Python embebido
REM Usa el Python del sistema para máxima compatibilidad
REM ===================================================================

SETLOCAL EnableDelayedExpansion

set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

title Creador de Monitor Simple

echo %GREEN%=========================================================%RESET%
echo %GREEN%   CREADOR DE MONITOR SIMPLE%RESET%
echo %GREEN%   Version que usa Python del sistema%RESET%
echo %GREEN%=========================================================%RESET%
echo.

cd /d "%~dp0"

REM Verificar si Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%ERROR: Python no está disponible en este sistema%RESET%
    echo.
    echo %YELLOW%Opciones para obtener Python:%RESET%
    echo 1. Microsoft Store: "python" ^(no requiere admin^)
    echo 2. python.org: Descargar Python portable
    echo 3. WinPython: Version portable
    echo.
    pause
    exit /b 1
)

echo %GREEN%✓ Python detectado:%RESET%
python --version
echo.

REM Crear carpeta del monitor simple
if not exist "MONITOR_SIMPLE" mkdir "MONITOR_SIMPLE"

echo %YELLOW%Creando monitor simple...%RESET%

REM Copiar archivos necesarios
copy "monitor_ultra_portable.py" "MONITOR_SIMPLE\" >nul
copy "quadient_sender_simple.py" "MONITOR_SIMPLE\" >nul 2>nul

REM Crear configuración simple
(
    echo # Configuracion del Monitor Simple
    echo # Edite estos valores según sus necesidades
    echo.
    echo # Procesos sospechosos a detectar ^(agregue los que necesite^)
    echo SUSPICIOUS_PROCESSES = [
    echo     'malware.exe', 'virus.exe', 'trojan.exe', 'keylogger.exe',
    echo     'hack.exe', 'crack.exe', 'suspicious.exe', 'backdoor.exe',
    echo     'rat.exe', 'spyware.exe', 'rootkit.exe'
    echo ]
    echo.
    echo # Carpetas a monitorear
    echo MONITOR_DIRS = [
    echo     'Desktop', 'Downloads', 'Documents', 'AppData/Local/Temp'
    echo ]
    echo.
    echo # Configuracion de email ^(opcional^)
    echo EMAIL_ENABLED = False
    echo EMAIL_SMTP = 'smtp.gmail.com'
    echo EMAIL_USER = ''
    echo EMAIL_PASS = ''
    echo EMAIL_TO = ''
    echo.
    echo # Webhook ^(opcional^)
    echo WEBHOOK_URL = ''
    echo.
    echo # Intervalo de verificacion ^(segundos^)
    echo CHECK_INTERVAL = 30
) > "MONITOR_SIMPLE\config_simple.py"

REM Crear launcher mejorado
(
    echo @echo off
    echo title Monitor Simple de Eventos
    echo.
    echo echo ████████████████████████████████████████████████████████████████
    echo echo    MONITOR SIMPLE DE EVENTOS WINDOWS
    echo echo    Version que usa Python del sistema
    echo echo ████████████████████████████████████████████████████████████████
    echo echo.
    echo echo 🔐 Sin permisos administrativos
    echo echo 📱 Usa Python del sistema
    echo echo 🚀 Completamente funcional
    echo echo 💾 Logs automáticos
    echo echo.
    echo.
    echo REM Verificar Python
    echo python --version ^>nul 2^>^&1
    echo if errorlevel 1 ^(
    echo     echo ❌ ERROR: Python no disponible
    echo     echo Instale Python desde Microsoft Store
    echo     pause
    echo     exit /b 1
    echo ^)
    echo.
    echo echo ✅ Python disponible:
    echo python --version
    echo echo.
    echo echo 🚀 Iniciando monitor...
    echo echo ⚠️  Presione Ctrl+C para detener
    echo echo 📁 Logs se guardan automáticamente
    echo echo.
    echo.
    echo cd /d "%%~dp0"
    echo python monitor_ultra_portable.py
    echo.
    echo echo.
    echo echo 🛑 Monitor detenido
    echo pause
) > "MONITOR_SIMPLE\EJECUTAR_MONITOR.bat"

REM Crear script de prueba rápida
(
    echo @echo off
    echo title Prueba Rápida del Monitor
    echo echo Ejecutando prueba rápida del monitor...
    echo echo.
    echo cd /d "%%~dp0"
    echo.
    echo python --version
    echo echo.
    echo echo Probando importaciones básicas...
    echo python -c "import os, sys, time, threading; print('✓ Importaciones básicas OK'^)"
    echo.
    echo echo Probando monitor ^(10 segundos^)...
    echo timeout /t 10 /nobreak ^| python monitor_ultra_portable.py ^>nul 2^>^&1
    echo echo ✓ Prueba completada
    echo.
    echo pause
) > "MONITOR_SIMPLE\PROBAR_RAPIDO.bat"

REM Crear documentación simple
(
    echo # Monitor Simple de Eventos Windows
    echo.
    echo ## Como usar:
    echo.
    echo 1. Ejecute EJECUTAR_MONITOR.bat
    echo 2. El monitor iniciará automáticamente
    echo 3. Presione Ctrl+C para detener
    echo.
    echo ## Que monitorea:
    echo.
    echo - Procesos sospechosos ^(malware, virus, trojans^)
    echo - Archivos sospechosos en carpetas del usuario
    echo - Conexiones de red sospechosas
    echo - Alto uso de CPU/Memoria
    echo.
    echo ## Configuración:
    echo.
    echo - Edite config_simple.py para personalizar
    echo - Configure email si desea alertas por correo
    echo - Configure webhook para Slack/Discord
    echo.
    echo ## Ventajas:
    echo.
    echo - NO requiere permisos administrativos
    echo - Usa Python del sistema ^(más estable^)
    echo - Completamente portable
    echo - Sin problemas de dependencias
    echo.
    echo ## Limitaciones:
    echo.
    echo - No puede acceder a Event Log de Windows
    echo - Solo monitorea carpetas del usuario
    echo - Requiere Python instalado en el sistema
    echo.
    echo Este monitor es ideal para usar en equipos donde
    echo no se tienen permisos administrativos pero hay
    echo Python disponible.
) > "MONITOR_SIMPLE\README.txt"

REM Probar que funciona
echo %YELLOW%Probando que el monitor funciona...%RESET%
cd "MONITOR_SIMPLE"
timeout /t 3 /nobreak | python monitor_ultra_portable.py >nul 2>&1
if errorlevel 1 (
    echo %RED%⚠️ Advertencia: El monitor puede tener problemas%RESET%
    echo Revise que Python funcione correctamente
) else (
    echo %GREEN%✓ Monitor simple funciona correctamente%RESET%
)
cd ..

echo.
echo %GREEN%=====================================================%RESET%
echo %GREEN%  MONITOR SIMPLE CREADO EXITOSAMENTE%RESET%
echo %GREEN%=====================================================%RESET%
echo.
echo %YELLOW%La carpeta MONITOR_SIMPLE contiene:%RESET%
echo.
echo  %BLUE%📄 monitor_ultra_portable.py%RESET%   - Monitor principal
echo  %BLUE%⚙️ config_simple.py%RESET%           - Configuración
echo  %BLUE%🚀 EJECUTAR_MONITOR.bat%RESET%       - Iniciar monitor
echo  %BLUE%🔧 PROBAR_RAPIDO.bat%RESET%          - Prueba rápida
echo  %BLUE%📖 README.txt%RESET%                 - Documentación
echo.
echo %GREEN%VENTAJAS DE ESTA VERSION:%RESET%
echo.
echo ✅ %YELLOW%NO requiere permisos administrativos%RESET%
echo ✅ %YELLOW%Usa Python del sistema ^(más estable^)%RESET%
echo ✅ %YELLOW%Sin problemas de Python embebido%RESET%
echo ✅ %YELLOW%Completamente portable%RESET%
echo ✅ %YELLOW%Detección efectiva de amenazas%RESET%
echo.
echo %BLUE%INSTRUCCIONES:%RESET%
echo.
echo 1. %YELLOW%Copie la carpeta MONITOR_SIMPLE%RESET% donde necesite
echo 2. %YELLOW%Ejecute EJECUTAR_MONITOR.bat%RESET%
echo 3. %YELLOW%¡Funciona inmediatamente!%RESET%
echo.
pause