@echo off
title Prueba del Monitor Portable
echo ====================================================
echo   PRUEBA DEL MONITOR PORTABLE
echo ====================================================
echo.
cd /d "%~dp0"

echo Verificando Python embebido...
"python-embedded\python.exe" --version
if errorlevel 1 (
    echo ERROR: Python embebido no funciona
    pause
    exit /b 1
)

echo.
echo Verificando dependencias...
"python-embedded\python.exe" -c "import psutil; print('psutil OK')"
"python-embedded\python.exe" -c "import requests; print('requests OK')"
if errorlevel 1 (
    echo ERROR: Faltan dependencias
    pause
    exit /b 1
)

echo.
echo Probando importacion del monitor...
"python-embedded\python.exe" -c "import sys; sys.path.append('.'); import portable_monitor; print('portable_monitor OK')"
if errorlevel 1 (
    echo ERROR: No se puede importar portable_monitor
    pause
    exit /b 1
)

echo.
echo Enviando alerta de prueba a Slack...
"python-embedded\python.exe" -c "import requests; response = requests.post('https://hooks.slack.com/services/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', json={'text': 'Test desde PROBAR_MONITOR.bat - Sistema funcionando', 'username': 'Security Monitor', 'icon_emoji': ':white_check_mark:'}); print('Slack:', 'OK' if response.status_code == 200 else 'ERROR')"

echo.
echo Probando monitor (5 segundos)...
echo Presione Ctrl+C para detener antes...
timeout /t 5 /nobreak | "python-embedded\python.exe" portable_monitor.py

echo.
echo ====================================================
echo   PRUEBA COMPLETADA EXITOSAMENTE
echo ====================================================
pause
