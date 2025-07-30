@echo off
REM Script para probar el funcionamiento del monitor portable

SETLOCAL EnableDelayedExpansion

set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

title Test de Monitor Portable

echo %GREEN%=========================================================%RESET%
echo %GREEN%   TEST DE MONITOR PORTABLE%RESET%
echo %GREEN%=========================================================%RESET%
echo.

cd /d "%~dp0"

REM Verificar que Python embebido esté instalado
if not exist "python-embedded\python.exe" (
    echo %RED%ERROR: Python embebido no encontrado.%RESET%
    echo Ejecute primero INSTALAR_PORTABLE.bat para configurar el entorno.
    pause
    exit /b 1
)

echo %YELLOW%Verificando Python embebido...%RESET%
"python-embedded\python.exe" --version
if errorlevel 1 (
    echo %RED%ERROR: Python embebido no funciona correctamente.%RESET%
    pause
    exit /b 1
)
echo Python embebido OK.

echo.
echo %YELLOW%Verificando módulos instalados...%RESET%
"python-embedded\python.exe" -c "import requests; import configparser; print('Módulos básicos: OK')"
if errorlevel 1 (
    echo %RED%ERROR: Faltan módulos necesarios.%RESET%
    echo Intente ejecutar INSTALAR_PORTABLE.bat de nuevo.
    pause
    exit /b 1
)

echo.
echo %YELLOW%Verificando configuración...%RESET%
if not exist "config.ini" (
    echo %RED%ERROR: No se encontró el archivo config.ini%RESET%
    pause
    exit /b 1
)

echo.
echo %YELLOW%Verificando script principal...%RESET%
if not exist "server_monitor.py" (
    echo %RED%ERROR: No se encontró el script principal server_monitor.py%RESET%
    pause
    exit /b 1
)

echo.
echo %YELLOW%Ejecutando una prueba rápida del monitor...%RESET%
echo (Esto verificará que el monitor puede iniciarse correctamente)
echo.

"python-embedded\python.exe" -c "import sys; import os; sys.path.append(os.getcwd()); import server_monitor; print('Monitor importado correctamente')"
if errorlevel 1 (
    echo %RED%ERROR: No se pudo importar el módulo server_monitor.%RESET%
    echo Es posible que haya errores en el código o dependencias faltantes.
    pause
    exit /b 1
)

echo.
echo %GREEN%=========================================================%RESET%
echo %GREEN%   TODAS LAS PRUEBAS PASARON EXITOSAMENTE%RESET%
echo %GREEN%=========================================================%RESET%
echo.
echo El sistema está configurado correctamente y listo para usarse.
echo.
echo Para ejecutar el monitor, use:
echo   %YELLOW%ejecutar_monitor_portable.bat%RESET% (ejecución visible)
echo   %YELLOW%ejecutar_monitor_portable_background.ps1%RESET% (en segundo plano)
echo.
echo Para configurar inicio automático, use:
echo   %YELLOW%configurar_inicio_portable.ps1%RESET%
echo.
pause
