@echo off
REM ===================================================================
REM MONITOR ULTRA PORTABLE - SIN PERMISOS ADMINISTRATIVOS
REM Funciona solo con Python estándar - NO requiere instalaciones
REM ===================================================================

title Monitor Ultra Portable de Eventos Windows

echo.
echo ████████████████████████████████████████████████████████████████
echo    MONITOR ULTRA PORTABLE DE EVENTOS WINDOWS
echo    Version SIN permisos administrativos
echo ████████████████████████████████████████████████████████████████
echo.
echo 🔐 Funciona sin permisos administrativos
echo 📱 Solo requiere Python estándar de Windows
echo 🚀 Completamente portable
echo 💾 No deja rastros en el sistema
echo.

REM Verificar si Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está disponible en este sistema
    echo.
    echo Opciones:
    echo 1. Use la version con Python embebido: CREAR_PORTABLE_COMPLETO.bat
    echo 2. Instale Python desde Microsoft Store ^(no requiere admin^)
    echo 3. Use Python portable desde PortableApps.com
    echo.
    pause
    exit /b 1
)

REM Mostrar versión de Python
echo ✅ Python detectado:
python --version
echo.

REM Preguntar por configuración
set /p config="¿Desea configurar email/webhook? (s/N): "
if /i "%config%"=="s" (
    set setup_flag=--setup
) else (
    set setup_flag=
)

echo.
echo 🚀 Iniciando Monitor Ultra Portable...
echo ⚠️  Presione Ctrl+C para detener
echo 📁 Los logs se guardan automáticamente
echo.

REM Ejecutar el monitor
cd /d "%~dp0"
python monitor_ultra_portable.py %setup_flag%

echo.
echo 🛑 Monitor detenido
pause