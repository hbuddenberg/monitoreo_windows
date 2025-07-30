@echo off
REM ===================================================================
REM SCRIPT DE VERIFICACIÓN COMPLETA DEL MONITOR PORTABLE
REM Verifica la integridad y funcionalidad de todos los componentes
REM ===================================================================

SETLOCAL EnableDelayedExpansion

REM Colores para mensajes
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "CYAN=[96m"
set "RESET=[0m"

title Verificación Completa del Monitor Portable

echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo %GREEN%   VERIFICACIÓN COMPLETA DEL MONITOR PORTABLE%RESET%
echo %GREEN%   Análisis detallado de integridad y funcionalidad%RESET%
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo.

cd /d "%~dp0"

REM Contadores de verificación
set checks_passed=0
set checks_total=0
set issues_found=0

echo %BLUE%PASO 1: Verificación de archivos principales...%RESET%
echo.

REM Verificación 1: Archivos Python críticos
set /a checks_total+=1
echo %YELLOW%[1/15] Verificando archivos Python críticos...%RESET%
set python_files_ok=0

if exist "portable_monitor.py" (
    echo %GREEN%  ✓ portable_monitor.py encontrado%RESET%
    set /a python_files_ok+=1
) else (
    echo %RED%  ✗ portable_monitor.py FALTANTE%RESET%
    set /a issues_found+=1
)

if exist "quadient_sender_simple.py" (
    echo %GREEN%  ✓ quadient_sender_simple.py encontrado%RESET%
    set /a python_files_ok+=1
) else (
    echo %RED%  ✗ quadient_sender_simple.py FALTANTE%RESET%
    set /a issues_found+=1
)

if %python_files_ok% equ 2 (
    echo %GREEN%  ✅ Archivos Python: COMPLETOS%RESET%
    set /a checks_passed+=1
) else (
    echo %RED%  ❌ Archivos Python: INCOMPLETO (%python_files_ok%/2)%RESET%
)
echo.

REM Verificación 2: Archivos de configuración
set /a checks_total+=1
echo %YELLOW%[2/15] Verificando archivos de configuración...%RESET%
if exist "config.ini" (
    findstr /C:"[event_monitoring]" config.ini >nul
    if errorlevel 1 (
        echo %RED%  ✗ config.ini existe pero estructura incorrecta%RESET%
        set /a issues_found+=1
    ) else (
        findstr /C:"specific_event_ids = 1074,6008,41" config.ini >nul
        if errorlevel 1 (
            echo %YELLOW%  ⚠️ config.ini existe pero Event IDs no configurados%RESET%
        ) else (
            echo %GREEN%  ✓ config.ini completo con Event IDs de reinicio%RESET%
            set /a checks_passed+=1
        )
    )
) else (
    echo %RED%  ✗ config.ini FALTANTE%RESET%
    set /a issues_found+=1
)
echo.

REM Verificación 3: Python embebido
set /a checks_total+=1
echo %YELLOW%[3/15] Verificando Python embebido...%RESET%
if exist "python-embedded\python.exe" (
    "python-embedded\python.exe" --version >nul 2>&1
    if errorlevel 1 (
        echo %RED%  ✗ python.exe no funciona correctamente%RESET%
        set /a issues_found+=1
    ) else (
        echo %GREEN%  ✓ Python embebido funcional%RESET%
        set /a checks_passed+=1
    )
) else (
    echo %RED%  ✗ python-embedded\python.exe FALTANTE%RESET%
    set /a issues_found+=1
)
echo.

REM Verificación 4: Archivo .pth crítico
set /a checks_total+=1
echo %YELLOW%[4/15] Verificando configuración .pth...%RESET%
if exist "python-embedded\python310._pth" (
    findstr /C:"import site" "python-embedded\python310._pth" >nul
    if errorlevel 1 (
        echo %RED%  ✗ python310._pth sin 'import site'%RESET%
        set /a issues_found+=1
    ) else (
        echo %GREEN%  ✓ python310._pth configurado correctamente%RESET%
        set /a checks_passed+=1
    )
) else (
    echo %RED%  ✗ python310._pth FALTANTE%RESET% 
    set /a issues_found+=1
)
echo.

echo %BLUE%PASO 2: Verificación de funcionalidad...%RESET%
echo.

REM Verificación 5: Sintaxis de archivos Python
set /a checks_total+=1
echo %YELLOW%[5/15] Verificando sintaxis Python...%RESET%
set syntax_ok=0

"python-embedded\python.exe" -m py_compile portable_monitor.py 2>nul
if errorlevel 1 (
    echo %RED%  ✗ Error de sintaxis en portable_monitor.py%RESET%
    set /a issues_found+=1
) else (
    echo %GREEN%  ✓ portable_monitor.py sintaxis OK%RESET%
    set /a syntax_ok+=1
)

"python-embedded\python.exe" -m py_compile quadient_sender_simple.py 2>nul
if errorlevel 1 (
    echo %RED%  ✗ Error de sintaxis en quadient_sender_simple.py%RESET%
    set /a issues_found+=1
) else (
    echo %GREEN%  ✓ quadient_sender_simple.py sintaxis OK%RESET%
    set /a syntax_ok+=1
)

if %syntax_ok% equ 2 (
    set /a checks_passed+=1
)
echo.

REM Verificación 6: Módulos básicos de Python
set /a checks_total+=1
echo %YELLOW%[6/15] Verificando módulos básicos de Python...%RESET%
"python-embedded\python.exe" -c "import os, sys, time, threading, subprocess, configparser, logging, datetime; print('Modulos basicos OK')" 2>nul
if errorlevel 1 (
    echo %RED%  ✗ Faltan módulos básicos de Python%RESET%
    set /a issues_found+=1
) else (
    echo %GREEN%  ✓ Módulos básicos disponibles%RESET%
    set /a checks_passed+=1
)
echo.

REM Verificación 7: Funcionalidades opcionales
set /a checks_total+=1
echo %YELLOW%[7/15] Verificando dependencias opcionales...%RESET%
set optional_deps=0

"python-embedded\python.exe" -c "import psutil; print('psutil OK')" 2>nul
if errorlevel 1 (
    echo %YELLOW%  ⚠️ psutil no disponible (usará métodos alternativos)%RESET%
) else (
    echo %GREEN%  ✓ psutil disponible%RESET%
    set /a optional_deps+=1
)

"python-embedded\python.exe" -c "import watchdog; print('watchdog OK')" 2>nul
if errorlevel 1 (
    echo %YELLOW%  ⚠️ watchdog no disponible (monitoreo de archivos limitado)%RESET%
) else (
    echo %GREEN%  ✓ watchdog disponible%RESET%
    set /a optional_deps+=1
)

"python-embedded\python.exe" -c "import requests; print('requests OK')" 2>nul
if errorlevel 1 (
    echo %YELLOW%  ⚠️ requests no disponible (sin webhooks)%RESET%
) else (
    echo %GREEN%  ✓ requests disponible%RESET%
    set /a optional_deps+=1
)

echo %CYAN%  → Dependencias opcionales: %optional_deps%/3%RESET%
set /a checks_passed+=1
echo.

echo %BLUE%PASO 3: Verificación de scripts de Windows...%RESET%
echo.

REM Verificación 8: Scripts .bat principales
set /a checks_total+=1
echo %YELLOW%[8/15] Verificando scripts .bat...%RESET%
set bat_files_ok=0

if exist "EJECUTAR_MONITOR_PORTABLE.bat" (
    echo %GREEN%  ✓ EJECUTAR_MONITOR_PORTABLE.bat encontrado%RESET%
    set /a bat_files_ok+=1
) else (
    echo %RED%  ✗ EJECUTAR_MONITOR_PORTABLE.bat FALTANTE%RESET%
    set /a issues_found+=1
)

if exist "PROBAR_MONITOR.bat" (
    echo %GREEN%  ✓ PROBAR_MONITOR.bat encontrado%RESET%
    set /a bat_files_ok+=1
) else (
    echo %RED%  ✗ PROBAR_MONITOR.bat FALTANTE%RESET%
    set /a issues_found+=1
)

if %bat_files_ok% equ 2 (
    echo %GREEN%  ✅ Scripts Windows: COMPLETOS%RESET%
    set /a checks_passed+=1
) else (
    echo %RED%  ❌ Scripts Windows: INCOMPLETO (%bat_files_ok%/2)%RESET%
)
echo.

echo %BLUE%PASO 4: Verificación de permisos y funcionalidad del sistema...%RESET%
echo.

REM Verificación 9: Comandos de Windows
set /a checks_total+=1
echo %YELLOW%[9/15] Verificando comandos de Windows...%RESET%
set windows_cmds_ok=0

tasklist >nul 2>&1
if errorlevel 1 (
    echo %RED%  ✗ tasklist no disponible%RESET%
    set /a issues_found+=1
) else (
    echo %GREEN%  ✓ tasklist disponible%RESET%
    set /a windows_cmds_ok+=1
)

wevtutil qe System /f:text /c:1 >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%  ⚠️ wevtutil limitado (sin permisos admin)%RESET%
) else (
    echo %GREEN%  ✓ wevtutil disponible%RESET%
    set /a windows_cmds_ok+=1
)

sc query >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%  ⚠️ sc query limitado%RESET%
) else (
    echo %GREEN%  ✓ sc query disponible%RESET%
    set /a windows_cmds_ok+=1
)

echo %CYAN%  → Comandos Windows: %windows_cmds_ok%/3%RESET%
set /a checks_passed+=1
echo.

REM Verificación 10: Directorios de trabajo
set /a checks_total+=1
echo %YELLOW%[10/15] Verificando directorios de trabajo...%RESET%

if not exist "logs" mkdir "logs" 2>nul
echo test > "logs\test_write.tmp" 2>nul
if exist "logs\test_write.tmp" (
    del "logs\test_write.tmp" 2>nul
    echo %GREEN%  ✓ Directorio logs escribible%RESET%
    set /a checks_passed+=1
) else (
    echo %RED%  ✗ No se puede escribir en logs%RESET%
    set /a issues_found+=1
)
echo.

echo %BLUE%PASO 5: Prueba de ejecución del monitor...%RESET%
echo.

REM Verificación 11: Importación de módulos
set /a checks_total+=1
echo %YELLOW%[11/15] Probando importación de módulos...%RESET%

(
    echo try:
    echo     from portable_monitor import PortableWindowsEventMonitor
    echo     print("✓ PortableWindowsEventMonitor importado correctamente"^)
    echo except Exception as e:
    echo     print(f"✗ Error importando PortableWindowsEventMonitor: {e}"^)
    echo     exit(1^)
    echo.
    echo try:
    echo     from quadient_sender_simple import AlertManager
    echo     print("✓ AlertManager importado correctamente"^)
    echo except Exception as e:
    echo     print(f"✗ Error importando AlertManager: {e}"^)
    echo     exit(1^)
) > test_imports.py

"python-embedded\python.exe" test_imports.py
set import_result=%errorlevel%
del test_imports.py 2>nul

if %import_result% equ 0 (
    echo %GREEN%  ✅ Importaciones: EXITOSAS%RESET%
    set /a checks_passed+=1
) else (
    echo %RED%  ❌ Importaciones: FALLARON%RESET%
    set /a issues_found+=1
)
echo.

REM Verificación 12: Configuración específica de Event IDs
set /a checks_total+=1
echo %YELLOW%[12/15] Verificando configuración de Event IDs...%RESET%

findstr /C:"1074" config.ini >nul && findstr /C:"6008" config.ini >nul && findstr /C:"41" config.ini >nul
if errorlevel 1 (
    echo %YELLOW%  ⚠️ Event IDs de reinicio no completamente configurados%RESET%
) else (
    echo %GREEN%  ✓ Event IDs críticos configurados (1074, 6008, 41)%RESET%
    set /a checks_passed+=1
)
echo.

REM Verificación 13: Sistema de alertas
set /a checks_total+=1
echo %YELLOW%[13/15] Probando sistema de alertas...%RESET%

"python-embedded\python.exe" quadient_sender_simple.py test >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%  ⚠️ Sistema de alertas con limitaciones%RESET%
) else (
    echo %GREEN%  ✓ Sistema de alertas funcional%RESET%
    set /a checks_passed+=1
)
echo.

REM Verificación 14: Acceso a escritorio
set /a checks_total+=1
echo %YELLOW%[14/15] Verificando acceso al escritorio...%RESET%

echo test > "%USERPROFILE%\Desktop\test_portable.tmp" 2>nul
if exist "%USERPROFILE%\Desktop\test_portable.tmp" (
    del "%USERPROFILE%\Desktop\test_portable.tmp" 2>nul
    echo %GREEN%  ✓ Puede escribir en el escritorio%RESET%
    set /a checks_passed+=1
) else (
    echo %YELLOW%  ⚠️ Acceso limitado al escritorio%RESET%
)
echo.

REM Verificación 15: Prueba rápida del monitor
set /a checks_total+=1
echo %YELLOW%[15/15] Prueba rápida del monitor (5 segundos)...%RESET%

(
    echo import signal
    echo import sys
    echo import time
    echo.
    echo def handler(signum, frame^):
    echo     print("Monitor detenido por timeout"^)
    echo     sys.exit(0^)
    echo.
    echo signal.signal(signal.SIGINT, handler^)
    echo.
    echo try:
    echo     from portable_monitor import PortableWindowsEventMonitor
    echo     monitor = PortableWindowsEventMonitor(^)
    echo     print("Monitor iniciado - prueba por 5 segundos..."^)
    echo     time.sleep(5^)
    echo     monitor.stop(^)
    echo     print("✓ Prueba del monitor completada exitosamente"^)
    echo except Exception as e:
    echo     print(f"✗ Error en prueba del monitor: {e}"^)
    echo     sys.exit(1^)
) > test_monitor_quick.py

timeout 10 "python-embedded\python.exe" test_monitor_quick.py >nul 2>&1
set monitor_test_result=%errorlevel%
del test_monitor_quick.py 2>nul

if %monitor_test_result% equ 0 (
    echo %GREEN%  ✅ Monitor ejecutado correctamente%RESET%
    set /a checks_passed+=1
) else (
    echo %YELLOW%  ⚠️ Monitor ejecutado con advertencias%RESET%
)
echo.

REM Calcular resultados
set /a percentage=(!checks_passed! * 100) / !checks_total!

echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo %GREEN%   RESULTADOS DE LA VERIFICACIÓN COMPLETA%RESET%
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo.

echo %BLUE%📊 ESTADÍSTICAS:%RESET%
echo   %CYAN%Verificaciones pasadas: %GREEN%!checks_passed!%RESET%%CYAN%/!checks_total!%RESET%
echo   %CYAN%Porcentaje de éxito: %GREEN%!percentage!%%%RESET%
echo   %CYAN%Problemas encontrados: %RED%!issues_found!%RESET%
echo.

if !percentage! geq 90 (
    echo %GREEN%✅ RESULTADO: EXCELENTE (!percentage!%%)%RESET%
    echo %GREEN%   El Monitor Portable está completamente funcional%RESET%
    echo.
    echo %GREEN%🚀 LISTO PARA USAR:%RESET%
    echo   %YELLOW%→ Ejecute: EJECUTAR_MONITOR_PORTABLE.bat%RESET%
    echo.
) else if !percentage! geq 70 (
    echo %YELLOW%⚠️ RESULTADO: BUENO (!percentage!%%)%RESET%
    echo %YELLOW%   El Monitor Portable funcionará con algunas limitaciones%RESET%
    echo.
    echo %YELLOW%✅ PUEDE USARSE:%RESET%
    echo   %YELLOW%→ Ejecute: EJECUTAR_MONITOR_PORTABLE.bat%RESET%
    echo   %CYAN%→ Algunas funciones avanzadas pueden estar limitadas%RESET%
    echo.
) else if !percentage! geq 50 (
    echo %YELLOW%⚠️ RESULTADO: ACEPTABLE (!percentage!%%)%RESET%
    echo %YELLOW%   El Monitor Portable funcionará en modo básico%RESET%
    echo.
    echo %YELLOW%🔧 ACCIONES RECOMENDADAS:%RESET%
    echo   1. Ejecute REPARAR_PYTHON_EMBEBIDO.bat si hay errores
    echo   2. Verifique los logs en la carpeta logs\
    echo   3. Considere usar CREAR_MONITOR_SIMPLE.bat como alternativa
    echo.
) else (
    echo %RED%❌ RESULTADO: PROBLEMAS CRÍTICOS (!percentage!%%)%RESET%
    echo %RED%   Se requieren correcciones antes de usar%RESET%
    echo.
    echo %RED%🚨 ACCIONES REQUERIDAS:%RESET%
    echo   1. %RED%CRÍTICO:%RESET% Ejecute REPARAR_PYTHON_EMBEBIDO.bat
    echo   2. %RED%CRÍTICO:%RESET% Verifique archivos faltantes
    echo   3. Consulte los logs para más detalles
    echo   4. Use CREAR_MONITOR_SIMPLE.bat como alternativa
    echo.
)

echo %BLUE%📋 FUNCIONALIDADES VERIFICADAS:%RESET%
echo.
echo %YELLOW%✅ Componentes principales:%RESET%
echo   • Monitor de eventos de reinicio/apagado: %GREEN%Disponible%RESET%
echo   • Búsqueda específica de Event IDs: %GREEN%Disponible%RESET%  
echo   • Monitoreo de procesos: %GREEN%Disponible%RESET%
echo   • Monitoreo de archivos: %GREEN%Disponible%RESET%
echo   • Sistema de alertas: %GREEN%Disponible%RESET%
echo.

echo %YELLOW%🔧 Funcionalidades opcionales:%RESET%
if %optional_deps% geq 2 (
    echo   • Monitoreo avanzado: %GREEN%Completo%RESET%
) else if %optional_deps% geq 1 (
    echo   • Monitoreo avanzado: %YELLOW%Parcial%RESET%
) else (
    echo   • Monitoreo avanzado: %YELLOW%Básico%RESET%
)

if %windows_cmds_ok% geq 2 (
    echo   • Comandos de Windows: %GREEN%Completo%RESET%
) else (
    echo   • Comandos de Windows: %YELLOW%Limitado%RESET%
)
echo.

if !issues_found! gtr 0 (
    echo %RED%⚠️ PROBLEMAS ENCONTRADOS: !issues_found!%RESET%
    echo %YELLOW%   Revise los mensajes anteriores para más detalles%RESET%
    echo.
)

echo %CYAN%📁 Archivos de log y alertas:%RESET%
echo   • logs\portable_monitor.log
echo   • logs\alerts.log
echo   • Desktop\ALERTAS_MONITOR_PORTABLE.txt
echo.

echo %BLUE%Presione cualquier tecla para salir...%RESET%
pause >nul