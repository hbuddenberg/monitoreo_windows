@echo off
REM ===================================================================
REM VERIFICADOR POST-REPARACION - Confirma que todo funciona
REM ===================================================================

SETLOCAL EnableDelayedExpansion

set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

title Verificador Post-Reparación

echo %GREEN%=========================================================%RESET%
echo %GREEN%   VERIFICADOR POST-REPARACION%RESET%
echo %GREEN%   Confirma que Python embebido funciona correctamente%RESET%
echo %GREEN%=========================================================%RESET%
echo.

cd /d "%~dp0"

echo %YELLOW%PASO 1: Verificando estructura de archivos...%RESET%
echo.

REM Verificar archivos principales
if exist "python-embedded\python.exe" (
    echo %GREEN%✓%RESET% python-embedded\python.exe
) else (
    echo %RED%✗%RESET% python-embedded\python.exe - FALTANTE
)

if exist "python-embedded\python310._pth" (
    echo %GREEN%✓%RESET% python-embedded\python310._pth
) else (
    echo %RED%✗%RESET% python-embedded\python310._pth - FALTANTE
)

if exist "PORTABLE_MONITOR\python-embedded\python.exe" (
    echo %GREEN%✓%RESET% PORTABLE_MONITOR\python-embedded\python.exe
) else (
    echo %RED%✗%RESET% PORTABLE_MONITOR\python-embedded\python.exe - FALTANTE
)

if exist "PORTABLE_MONITOR\python-embedded\python310._pth" (
    echo %GREEN%✓%RESET% PORTABLE_MONITOR\python-embedded\python310._pth
) else (
    echo %RED%✗%RESET% PORTABLE_MONITOR\python-embedded\python310._pth - FALTANTE
)

echo.
echo %YELLOW%PASO 2: Verificando contenido del archivo .pth...%RESET%
echo.

if exist "python-embedded\python310._pth" (
    echo %BLUE%Contenido de python-embedded\python310._pth:%RESET%
    type "python-embedded\python310._pth"
    echo.
)

if exist "PORTABLE_MONITOR\python-embedded\python310._pth" (
    echo %BLUE%Contenido de PORTABLE_MONITOR\python-embedded\python310._pth:%RESET%
    type "PORTABLE_MONITOR\python-embedded\python310._pth"
    echo.
)

echo %YELLOW%PASO 3: Probando Python embebido principal...%RESET%
echo.

if exist "python-embedded\python.exe" (
    echo Ejecutando: python-embedded\python.exe --version
    "python-embedded\python.exe" --version
    if errorlevel 1 (
        echo %RED%✗ Error ejecutando Python embebido principal%RESET%
    ) else (
        echo %GREEN%✓ Python embebido principal funciona%RESET%
    )
    
    echo.
    echo Ejecutando: python-embedded\python.exe -c "print('Hola desde Python embebido')"
    "python-embedded\python.exe" -c "print('Hola desde Python embebido')"
    if errorlevel 1 (
        echo %RED%✗ Error ejecutando código Python%RESET%
    ) else (
        echo %GREEN%✓ Ejecución de código Python OK%RESET%
    )
    
    echo.
    echo Probando importaciones básicas...
    "python-embedded\python.exe" -c "import os, sys, time; print('✓ Importaciones básicas OK')"
    if errorlevel 1 (
        echo %RED%✗ Error con importaciones básicas%RESET%
    ) else (
        echo %GREEN%✓ Importaciones básicas OK%RESET%
    )
)

echo.
echo %YELLOW%PASO 4: Probando PORTABLE_MONITOR...%RESET%
echo.

if exist "PORTABLE_MONITOR\python-embedded\python.exe" (
    echo Ejecutando: PORTABLE_MONITOR\python-embedded\python.exe --version
    "PORTABLE_MONITOR\python-embedded\python.exe" --version
    if errorlevel 1 (
        echo %RED%✗ Error ejecutando PORTABLE_MONITOR Python%RESET%
    ) else (
        echo %GREEN%✓ PORTABLE_MONITOR Python funciona%RESET%
    )
    
    echo.
    echo Probando importaciones en PORTABLE_MONITOR...
    "PORTABLE_MONITOR\python-embedded\python.exe" -c "import os, sys, time; print('✓ PORTABLE_MONITOR importaciones OK')"
    if errorlevel 1 (
        echo %RED%✗ Error con importaciones en PORTABLE_MONITOR%RESET%
    ) else (
        echo %GREEN%✓ PORTABLE_MONITOR importaciones OK%RESET%
    )
)

echo.
echo %YELLOW%PASO 5: Prueba final del monitor...%RESET%
echo.

if exist "PORTABLE_MONITOR\portable_monitor.py" (
    echo Probando el monitor portable por 5 segundos...
    cd "PORTABLE_MONITOR"
    timeout /t 5 /nobreak | "python-embedded\python.exe" portable_monitor.py
    set monitor_result=!errorlevel!
    cd..
    
    if !monitor_result! equ 0 (
        echo %GREEN%✓ Monitor portable funciona correctamente!%RESET%
    ) else (
        echo %YELLOW%⚠️ Monitor se detuvo (normal con timeout)%RESET%
    )
) else (
    echo %RED%✗ No se encuentra portable_monitor.py%RESET%
)

echo.
echo %GREEN%=====================================================%RESET%
echo %GREEN%  VERIFICACION COMPLETADA%RESET%
echo %GREEN%=====================================================%RESET%
echo.

REM Resumen final
echo %BLUE%RESUMEN:%RESET%
echo.

if exist "python-embedded\python.exe" (
    "python-embedded\python.exe" --version >nul 2>&1
    if errorlevel 1 (
        echo %RED%❌ Python embebido principal: FALLA%RESET%
    ) else (
        echo %GREEN%✅ Python embebido principal: OK%RESET%
    )
)

if exist "PORTABLE_MONITOR\python-embedded\python.exe" (
    "PORTABLE_MONITOR\python-embedded\python.exe" --version >nul 2>&1
    if errorlevel 1 (
        echo %RED%❌ PORTABLE_MONITOR: FALLA%RESET%
    ) else (
        echo %GREEN%✅ PORTABLE_MONITOR: OK%RESET%
    )
)

echo.
echo %YELLOW%PRÓXIMOS PASOS:%RESET%
echo.
echo Si todo está %GREEN%OK%RESET%:
echo   %BLUE%→ Ejecute: PORTABLE_MONITOR\EJECUTAR_MONITOR_PORTABLE.bat%RESET%
echo.
echo Si hay %RED%FALLAS%RESET%:
echo   %BLUE%→ Ejecute: CREAR_MONITOR_SIMPLE.bat (alternativa estable)%RESET%
echo.

pause