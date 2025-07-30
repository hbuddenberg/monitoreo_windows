@echo off
REM ===================================================================
REM REPARADOR DE PYTHON EMBEBIDO - Corrige el error de .pth
REM ===================================================================

SETLOCAL EnableDelayedExpansion

set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

title Reparador de Python Embebido

echo %GREEN%=========================================================%RESET%
echo %GREEN%   REPARADOR DE PYTHON EMBEBIDO%RESET%
echo %GREEN%   Corrige errores de configuracion%RESET%
echo %GREEN%=========================================================%RESET%
echo.

cd /d "%~dp0"

REM Verificar si existe Python embebido
if not exist "python-embedded\python.exe" (
    echo %RED%ERROR: No se encuentra Python embebido%RESET%
    echo Ejecute INSTALAR_PORTABLE.bat primero
    pause
    exit /b 1
)

if not exist "PORTABLE_MONITOR\python-embedded\python.exe" (
    echo %RED%ERROR: No se encuentra PORTABLE_MONITOR%RESET%
    echo Ejecute CREAR_PORTABLE_COMPLETO.bat primero
    pause
    exit /b 1
)

echo %YELLOW%Reparando archivo python310._pth...%RESET%

REM Reparar en python-embedded principal
if exist "python-embedded\python310._pth" (
    echo %YELLOW%Reparando python-embedded\python310._pth%RESET%
    (
        echo python310.zip
        echo .
        echo.
        echo # Uncomment to run site.main^(^) automatically
        echo import site
    ) > "python-embedded\python310._pth"
    echo %GREEN%✓ python-embedded\python310._pth reparado%RESET%
)

REM Reparar en PORTABLE_MONITOR
if exist "PORTABLE_MONITOR\python-embedded\python310._pth" (
    echo %YELLOW%Reparando PORTABLE_MONITOR\python-embedded\python310._pth%RESET%
    (
        echo python310.zip
        echo .
        echo.
        echo # Uncomment to run site.main^(^) automatically
        echo import site
    ) > "PORTABLE_MONITOR\python-embedded\python310._pth"
    echo %GREEN%✓ PORTABLE_MONITOR\python-embedded\python310._pth reparado%RESET%
)

echo.
echo %YELLOW%Probando Python embebido reparado...%RESET%

REM Probar python-embedded principal
if exist "python-embedded\python.exe" (
    echo Probando python-embedded principal:
    "python-embedded\python.exe" -c "print('✓ Python embebido principal OK')"
    if errorlevel 1 (
        echo %RED%✗ Aún hay problemas con python-embedded principal%RESET%
    ) else (
        echo %GREEN%✓ python-embedded principal funciona correctamente%RESET%
    )
)

echo.

REM Probar PORTABLE_MONITOR
if exist "PORTABLE_MONITOR\python-embedded\python.exe" (
    echo Probando PORTABLE_MONITOR:
    "PORTABLE_MONITOR\python-embedded\python.exe" -c "print('✓ Python embebido portable OK')"
    if errorlevel 1 (
        echo %RED%✗ Aún hay problemas con PORTABLE_MONITOR%RESET%
    ) else (
        echo %GREEN%✓ PORTABLE_MONITOR funciona correctamente%RESET%
    )
)

echo.
echo %GREEN%=====================================================%RESET%
echo %GREEN%  REPARACION COMPLETADA%RESET%
echo %GREEN%=====================================================%RESET%
echo.
echo Ahora puede ejecutar:
echo %YELLOW%- PORTABLE_MONITOR\EJECUTAR_MONITOR_PORTABLE.bat%RESET%
echo %YELLOW%- PORTABLE_MONITOR\PROBAR_MONITOR.bat%RESET%
echo.
pause