#!/usr/bin/env python3
"""
Script de Pruebas para el Sistema de Monitoreo de Eventos Windows
Verifica que todos los componentes estén funcionando correctamente.
"""

import os
import sys
import time
import tempfile
import configparser
import logging
from datetime import datetime

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Prueba que todos los módulos se importen correctamente"""
    print("🔍 Probando importaciones de módulos...")
    
    try:
        import windows_event_monitor
        print("  ✅ windows_event_monitor importado correctamente")
    except ImportError as e:
        print(f"  ❌ Error importando windows_event_monitor: {e}")
        return False
    
    try:
        import code_analyzer
        print("  ✅ code_analyzer importado correctamente")
    except ImportError as e:
        print(f"  ❌ Error importando code_analyzer: {e}")
        return False
    
    try:
        import quadient_sender_simple
        print("  ✅ quadient_sender_simple importado correctamente")
    except ImportError as e:
        print(f"  ❌ Error importando quadient_sender_simple: {e}")
        return False
    
    return True

def test_dependencies():
    """Prueba que las dependencias críticas estén disponibles"""
    print("\n🔍 Probando dependencias del sistema...")
    
    dependencies = [
        ('win32evtlog', 'pywin32'),
        ('wmi', 'WMI'),
        ('watchdog', 'watchdog'),
        ('requests', 'requests'),
        ('plyer', 'plyer (opcional)')
    ]
    
    all_ok = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"  ✅ {name} disponible")
        except ImportError:
            print(f"  ⚠️  {name} no disponible")
            if 'opcional' not in name:
                all_ok = False
    
    return all_ok

def test_config_file():
    """Prueba la carga del archivo de configuración"""
    print("\n🔍 Probando archivo de configuración...")
    
    config_file = 'config.ini'
    if not os.path.exists(config_file):
        print(f"  ❌ Archivo {config_file} no encontrado")
        return False
    
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        
        # Verificar secciones críticas
        required_sections = [
            'event_monitoring',
            'process_monitoring', 
            'file_monitoring',
            'code_analysis',
            'alerts'
        ]
        
        for section in required_sections:
            if config.has_section(section):
                print(f"  ✅ Sección [{section}] encontrada")
            else:
                print(f"  ❌ Sección [{section}] faltante")
                return False
                
        return True
        
    except Exception as e:
        print(f"  ❌ Error leyendo configuración: {e}")
        return False

def test_code_analyzer():
    """Prueba el analizador de código"""
    print("\n🔍 Probando analizador de código...")
    
    try:
        from code_analyzer import CodeAnalyzer
        
        # Configurar logger para pruebas
        logger = logging.getLogger('test')
        logger.setLevel(logging.ERROR)  # Solo errores para pruebas
        
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        analyzer = CodeAnalyzer(config, logger)
        
        # Crear archivo de prueba
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Este es un archivo de prueba\nContenido normal")
            test_file = f.name
        
        try:
            # Probar análisis
            is_suspicious = analyzer.is_suspicious_file(test_file)
            print(f"  ✅ Análisis de archivo completado (sospechoso: {is_suspicious})")
            
            # Probar reporte
            report = analyzer.get_analysis_report(test_file)
            if 'error' not in report:
                print("  ✅ Generación de reporte funcional")
            else:
                print(f"  ❌ Error en reporte: {report['error']}")
                return False
                
        finally:
            # Limpiar archivo de prueba
            os.unlink(test_file)
            
        return True
        
    except Exception as e:
        print(f"  ❌ Error probando analizador: {e}")
        return False

def test_alert_system():
    """Prueba el sistema de alertas"""
    print("\n🔍 Probando sistema de alertas...")
    
    try:
        from quadient_sender_simple import AlertManager
        
        alert_manager = AlertManager()
        
        # Crear datos de prueba
        test_data = {
            'type': 'system_test',
            'severity': 'LOW',
            'hostname': 'TEST-PC',
            'message': 'Prueba automática del sistema'
        }
        
        # Nota: no enviamos la alerta realmente para evitar spam
        # Solo verificamos que el objeto se cree correctamente
        print("  ✅ AlertManager inicializado correctamente")
        
        # Verificar métodos principales
        if hasattr(alert_manager, 'send_alert'):
            print("  ✅ Método send_alert disponible")
        else:
            print("  ❌ Método send_alert no encontrado")
            return False
            
        return True
        
    except Exception as e:
        print(f"  ❌ Error probando sistema de alertas: {e}")
        return False

def test_logs_directory():
    """Verifica que el directorio de logs exista y sea escribible"""
    print("\n🔍 Probando directorio de logs...")
    
    logs_dir = 'logs'
    
    try:
        # Crear directorio si no existe
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            print(f"  ✅ Directorio {logs_dir} creado")
        else:
            print(f"  ✅ Directorio {logs_dir} existe")
        
        # Probar escritura
        test_file = os.path.join(logs_dir, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write(f"Test {datetime.now()}")
        
        os.remove(test_file)
        print("  ✅ Directorio de logs es escribible")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error con directorio de logs: {e}")
        return False

def test_windows_event_monitor():
    """Prueba básica del monitor de eventos Windows"""
    print("\n🔍 Probando monitor de eventos Windows...")
    
    try:
        from windows_event_monitor import WindowsEventMonitor
        
        # Solo verificar que se puede inicializar
        monitor = WindowsEventMonitor()
        print("  ✅ WindowsEventMonitor inicializado correctamente")
        
        # Verificar componentes
        if hasattr(monitor, 'event_log_monitor'):
            print("  ✅ EventLogMonitor disponible")
        else:
            print("  ❌ EventLogMonitor no disponible")
            return False
            
        if hasattr(monitor, 'process_monitor'):
            print("  ✅ ProcessMonitor disponible")
        else:
            print("  ❌ ProcessMonitor no disponible")
            return False
            
        return True
        
    except Exception as e:
        print(f"  ❌ Error probando monitor de eventos: {e}")
        return False

def run_full_test():
    """Ejecuta todas las pruebas"""
    print("=" * 60)
    print("   PRUEBAS DEL SISTEMA DE MONITOREO DE EVENTOS WINDOWS")
    print("=" * 60)
    
    tests = [
        ("Importaciones", test_imports),
        ("Dependencias", test_dependencies),
        ("Configuración", test_config_file),
        ("Directorio de Logs", test_logs_directory),
        ("Analizador de Código", test_code_analyzer),
        ("Sistema de Alertas", test_alert_system),
        ("Monitor de Eventos", test_windows_event_monitor)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Error ejecutando prueba {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("   RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ EXITOSA" if result else "❌ FALLIDA"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Pruebas exitosas: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema está listo para usar.")
        return True
    else:
        print(f"\n⚠️  {total - passed} pruebas fallaron. Revise los errores arriba.")
        return False

if __name__ == "__main__":
    # Cambiar al directorio del script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    success = run_full_test()
    
    print("\n" + "=" * 60)
    if success:
        print("El sistema está completamente funcional.")
        print("\nPara iniciar el monitoreo:")
        print("  • Manual: ejecutar_monitor_portable.bat")
        print("  • Segundo plano: ejecutar_monitor_portable_background.ps1")
    else:
        print("Se encontraron problemas que deben resolverse.")
        print("\nRevise:")
        print("  • Que INSTALAR_PORTABLE.bat haya completado exitosamente")
        print("  • Que todas las dependencias estén instaladas")
        print("  • El archivo config.ini esté configurado correctamente")
    
    print("=" * 60)
    
    sys.exit(0 if success else 1)