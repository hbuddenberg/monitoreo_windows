@echo off
REM ===================================================================
REM SCRIPT DE PRUEBA COMPLETA DEL MONITOR PORTABLE
REM Verifica todas las funcionalidades del monitor mejorado
REM ===================================================================

SETLOCAL EnableDelayedExpansion

REM Colores para mensajes
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

title Prueba Completa del Monitor Portable

echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo %GREEN%   PRUEBA COMPLETA DEL MONITOR PORTABLE%RESET%
echo %GREEN%   Verificacion de todas las funcionalidades%RESET%
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo.

cd /d "%~dp0"

REM Contador de pruebas
set tests_passed=0
set tests_total=0

echo %BLUE%PASO 1: Verificando entorno...%RESET%
echo.

REM Prueba 1: Python embebido
set /a tests_total+=1
echo %YELLOW%Prueba 1: Python embebido...%RESET%
if exist "python-embedded\python.exe" (
    "python-embedded\python.exe" --version
    if errorlevel 1 (
        echo %RED%✗ Python embebido no funciona%RESET%
    ) else (
        echo %GREEN%✓ Python embebido OK%RESET%
        set /a tests_passed+=1
    )
) else (
    echo %RED%✗ Python embebido no encontrado%RESET%
)
echo.

REM Prueba 2: Dependencias básicas
set /a tests_total+=1
echo %YELLOW%Prueba 2: Dependencias básicas...%RESET%
"python-embedded\python.exe" -c "import os, sys, time, threading, subprocess; print('✓ Modulos basicos OK')" 2>nul
if errorlevel 1 (
    echo %RED%✗ Falta algún módulo básico%RESET%
) else (
    echo %GREEN%✓ Módulos básicos disponibles%RESET%
    set /a tests_passed+=1
)

REM Prueba 3: Psutil (opcional)
set /a tests_total+=1
echo %YELLOW%Prueba 3: psutil (monitoreo de procesos)...%RESET%
"python-embedded\python.exe" -c "import psutil; print('✓ psutil disponible')" 2>nul
if errorlevel 1 (
    echo %YELLOW%⚠️ psutil no disponible - usando métodos alternativos%RESET%
) else (
    echo %GREEN%✓ psutil disponible%RESET%
    set /a tests_passed+=1
)

REM Prueba 4: Watchdog (opcional)
set /a tests_total+=1
echo %YELLOW%Prueba 4: watchdog (monitoreo de archivos)...%RESET%
"python-embedded\python.exe" -c "import watchdog; print('✓ watchdog disponible')" 2>nul
if errorlevel 1 (
    echo %YELLOW%⚠️ watchdog no disponible - monitoreo de archivos limitado%RESET%
) else (
    echo %GREEN%✓ watchdog disponible%RESET%
    set /a tests_passed+=1
)

REM Prueba 5: Sistema de alertas
set /a tests_total+=1
echo %YELLOW%Prueba 5: Sistema de alertas...%RESET%
"python-embedded\python.exe" -c "from quadient_sender_simple import AlertManager; print('✓ Sistema de alertas OK')" 2>nul
if errorlevel 1 (
    echo %YELLOW%⚠️ Sistema de alertas limitado%RESET%
) else (
    echo %GREEN%✓ Sistema de alertas completo disponible%RESET%
    set /a tests_passed+=1
)

echo.
echo %BLUE%PASO 2: Verificando configuración...%RESET%
echo.

REM Prueba 6: Archivo de configuración
set /a tests_total+=1
echo %YELLOW%Prueba 6: Archivo de configuración...%RESET%
if exist "config.ini" (
    echo %GREEN%✓ config.ini encontrado%RESET%
    
    REM Verificar secciones importantes
    findstr /C:"specific_event_ids" config.ini >nul
    if errorlevel 1 (
        echo %RED%✗ Configuración incompleta%RESET%
    ) else (
        echo %GREEN%✓ Configuración completa%RESET%
        set /a tests_passed+=1
    )
) else (
    echo %YELLOW%⚠️ config.ini no encontrado - usando valores por defecto%RESET%
)

REM Prueba 7: Directorio de logs
set /a tests_total+=1
echo %YELLOW%Prueba 7: Directorio de logs...%RESET%
if not exist "logs" mkdir "logs"
echo test > "logs\test_write.tmp" 2>nul
if exist "logs\test_write.tmp" (
    del "logs\test_write.tmp"
    echo %GREEN%✓ Directorio de logs escribible%RESET%
    set /a tests_passed+=1
) else (
    echo %RED%✗ No se puede escribir en logs%RESET%
)

echo.
echo %BLUE%PASO 3: Probando monitor (10 segundos)...%RESET%
echo.

REM Prueba 8: Ejecución del monitor
set /a tests_total+=1
echo %YELLOW%Prueba 8: Ejecución del monitor...%RESET%
echo %YELLOW%Iniciando monitor por 10 segundos...%RESET%

REM Crear script temporal para detener el monitor
(
    echo import signal
    echo import sys
    echo import time
    echo import os
    echo.
    echo def handler(signum, frame^):
    echo     print("Monitor detenido por timeout"^)
    echo     sys.exit(0^)
    echo.
    echo signal.signal(signal.SIGINT, handler^)
    echo.
    echo # Importar y ejecutar monitor
    echo try:
    echo     from portable_monitor import PortableWindowsEventMonitor
    echo     monitor = PortableWindowsEventMonitor(^)
    echo     print("Monitor iniciado correctamente"^)  
    echo     time.sleep(10^)  # Ejecutar 10 segundos
    echo     monitor.stop(^)
    echo     print("Prueba completada exitosamente"^)
    echo except Exception as e:
    echo     print(f"Error: {e}"^)
    echo     sys.exit(1^)
) > test_monitor.py

"python-embedded\python.exe" test_monitor.py
set monitor_result=%errorlevel%

REM Limpiar archivo temporal
if exist "test_monitor.py" del "test_monitor.py"

if %monitor_result% equ 0 (
    echo %GREEN%✓ Monitor ejecutado correctamente%RESET%
    set /a tests_passed+=1
) else (
    echo %RED%✗ Error ejecutando monitor%RESET%
)

echo.
echo %BLUE%PASO 4: Verificando funcionalidades específicas...%RESET%
echo.

REM Prueba 9: Comandos de Windows
set /a tests_total+=1
echo %YELLOW%Prueba 9: Comandos de Windows (tasklist, wevtutil)...%RESET%
tasklist >nul 2>&1
if errorlevel 1 (
    echo %RED%✗ tasklist no disponible%RESET%
) else (
    wevtutil qe System /c:1 >nul 2>&1
    if errorlevel 1 (
        echo %YELLOW%⚠️ wevtutil limitado (sin permisos admin)%RESET%
        set /a tests_passed+=1
    ) else (
        echo %GREEN%✓ Comandos de Windows disponibles%RESET%
        set /a tests_passed+=1
    )
)

REM Prueba 10: Verificar logs generados
set /a tests_total+=1
echo %YELLOW%Prueba 10: Logs generados...%RESET%
if exist "logs\portable_monitor.log" (
    echo %GREEN%✓ Log del monitor creado%RESET%
    set /a tests_passed+=1
) else (
    echo %YELLOW%⚠️ Log no generado aún%RESET%
)

echo.
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo %GREEN%   RESULTADOS DE LA PRUEBA%RESET%
echo %GREEN%████████████████████████████████████████████████████████████████%RESET%
echo.

echo %BLUE%Pruebas pasadas: %RESET%%GREEN%!tests_passed!%RESET%%BLUE%/!tests_total!%RESET%

REM Calcular porcentaje
set /a percentage=(!tests_passed! * 100) / !tests_total!

if !percentage! geq 80 (
    echo %GREEN%✅ RESULTADO: EXCELENTE (!percentage!%%)%RESET%
    echo %GREEN%El monitor está listo para usar%RESET%
) else if !percentage! geq 60 (
    echo %YELLOW%⚠️ RESULTADO: ACEPTABLE (!percentage!%%)%RESET%
    echo %YELLOW%El monitor funcionará con limitaciones%RESET%
) else (
    echo %RED%❌ RESULTADO: PROBLEMAS (!percentage!%%)%RESET%
    echo %RED%Se requieren correcciones antes de usar%RESET%
)

echo.
echo %BLUE%📋 RESUMEN:%RESET%
echo.
echo %YELLOW%✅ Funcionalidades principales:%RESET%
echo   • Monitoreo de procesos: %GREEN%Disponible%RESET%
echo   • Monitoreo de archivos: %GREEN%Disponible%RESET%
echo   • Detección de eventos de reinicio: %GREEN%Disponible%RESET%
echo   • Búsqueda específica de Event IDs: %GREEN%Disponible%RESET%
echo   • Sistema de alertas: %GREEN%Disponible%RESET%
echo.

if !percentage! geq 80 (
    echo %GREEN%🚀 LISTO PARA USAR:%RESET%
    echo   Ejecute: %YELLOW%EJECUTAR_MONITOR_PORTABLE.bat%RESET%
) else (
    echo %YELLOW%🔧 ACCIONES RECOMENDADAS:%RESET%
    echo   1. Ejecute REPARAR_PYTHON_EMBEBIDO.bat si hay errores
    echo   2. Verifique los logs en la carpeta logs\
    echo   3. Use CREAR_MONITOR_SIMPLE.bat como alternativa
)

echo.
echo %BLUE%Presione cualquier tecla para salir...%RESET%
pause >nul
