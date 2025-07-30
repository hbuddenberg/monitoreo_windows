@echo off
title Monitor Portable de Eventos Windows
echo ========================================================
echo   MONITOR PORTABLE DE EVENTOS WINDOWS
echo   Version sin permisos administrativos
echo ========================================================
echo.
cd /d "%~dp0"

echo Iniciando monitor portable...
echo Presione Ctrl+C para detener
echo.
"python-embedded\python.exe" portable_monitor.py

if errorlevel 1 (
    echo ERROR: No se pudo iniciar el monitor.
    echo Verifique que Python embebido este disponible.
    pause
)
