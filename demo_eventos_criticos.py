#!/usr/bin/env python3
"""
Script de Demostración: Detección de Eventos Críticos del Sistema
Muestra cómo el sistema detecta eventos de reinicio/apagado y búsqueda específica de Event IDs.
"""

import os
import sys
import time
import configparser
import logging
from datetime import datetime, timedelta

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demonstrate_event_monitoring():
    """Demuestra las capacidades de monitoreo de eventos"""
    
    print("=" * 70)
    print("   DEMOSTRACIÓN: SISTEMA MEJORADO DE MONITOREO DE EVENTOS")
    print("=" * 70)
    print()
    
    # Verificar dependencias
    try:
        import win32evtlog
        import win32evtlogutil
        from windows_event_monitor import EventLogMonitor
        from quadient_sender_simple import AlertManager
    except ImportError as e:
        print(f"❌ Error: Dependencias faltantes - {e}")
        print("Ejecute el instalador portable primero.")
        return False
    
    # Cargar configuración
    config = configparser.ConfigParser()
    if not os.path.exists('config.ini'):
        print("❌ Error: Archivo config.ini no encontrado")
        return False
    
    config.read('config.ini')
    
    # Configurar logger
    logger = logging.getLogger('demo')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(handler)
    
    print("🔍 FUNCIONALIDADES IMPLEMENTADAS:")
    print()
    
    # 1. Demostrar eventos críticos de sistema
    print("1. 🚨 DETECCIÓN DE EVENTOS CRÍTICOS DE SISTEMA:")
    print("   - Reinicio/Apagado del sistema (Event IDs: 1074, 6005, 6006)")
    print("   - Fallos críticos (Event IDs: 6008, 41, 109)")
    print("   - Arranques del sistema (Event IDs: 12, 6005)")
    print("   - Información detallada de quien/qué inició el reinicio")
    print()
    
    # 2. Demostrar búsqueda específica
    print("2. 🎯 BÚSQUEDA ESPECÍFICA DE EVENT IDs:")
    print("   - Configurar 'specific_event_ids' en config.ini para eventos prioritarios")
    print("   - Si no se encuentran eventos específicos, busca en todos")
    print("   - Ejemplo: specific_event_ids = 1074,6008,41")
    print()
    
    # 3. Mostrar configuración actual
    print("3. ⚙️ CONFIGURACIÓN ACTUAL:")
    
    event_ids = config.get('event_monitoring', 'event_ids', fallback='N/A')
    specific_ids = config.get('event_monitoring', 'specific_event_ids', fallback='')
    search_all = config.getboolean('event_monitoring', 'search_all_if_not_found', fallback=True)
    sources = config.get('event_monitoring', 'sources', fallback='N/A')
    
    print(f"   - Event IDs regulares: {event_ids}")
    print(f"   - Event IDs específicos: {specific_ids if specific_ids else 'No configurados'}")
    print(f"   - Buscar todos si no encuentra específicos: {'Sí' if search_all else 'No'}")
    print(f"   - Fuentes monitoreadas: {sources}")
    print()
    
    # 4. Demostrar sistema de alertas mejorado
    print("4. 📧 SISTEMA DE ALERTAS MEJORADO:")
    print("   - Emails con información detallada del evento")
    print("   - Categorización automática (APAGADO/REINICIO, FALLO CRÍTICO, etc.)")
    print("   - Información adicional para eventos de shutdown")
    print("   - Diferentes niveles de severidad")
    print()
    
    # 5. Probar búsqueda de eventos recientes
    print("5. 📊 ANÁLISIS DE EVENTOS RECIENTES:")
    print("   Buscando eventos críticos en los últimos logs...")
    print()
    
    try:
        monitor = EventLogMonitor(config, logger)
        
        # Simular búsqueda de eventos recientes
        critical_events_found = search_recent_critical_events()
        
        if critical_events_found:
            print(f"   ✅ Se encontraron {len(critical_events_found)} eventos críticos recientes")
            for event in critical_events_found[:3]:  # Mostrar solo los primeros 3
                print(f"      - Event ID {event['id']}: {event['description']}")
        else:
            print("   ℹ️ No se encontraron eventos críticos recientes")
            
    except Exception as e:
        print(f"   ⚠️ Error accediendo a logs: {e}")
    
    print()
    
    # 6. Demostrar configuración de eventos específicos
    print("6. 🎛️ CÓMO CONFIGURAR EVENTOS ESPECÍFICOS:")
    print()
    print("   Para monitorear Event IDs específicos, edite config.ini:")
    print()
    print("   [event_monitoring]")
    print("   # Para buscar solo eventos de reinicio:")
    print("   specific_event_ids = 1074,6008,41")
    print()
    print("   # Para buscar un evento específico de su interés:")
    print("   specific_event_ids = 4625")
    print()
    print("   # Para buscar múltiples eventos críticos:")
    print("   specific_event_ids = 1074,4625,7034,6008")
    print()
    
    # 7. Mostrar tipos de eventos críticos
    print("7. 📋 EVENTOS CRÍTICOS MONITOREADOS AUTOMÁTICAMENTE:")
    print()
    
    critical_events = {
        1074: "Apagado/Reinicio iniciado por usuario o aplicación",
        6005: "Event Log Service iniciado (arranque del sistema)",
        6006: "Event Log Service detenido (apagado del sistema)", 
        6008: "Apagado inesperado del sistema",
        1076: "Apagado iniciado pero cancelado",
        6013: "Tiempo de actividad del sistema",
        12: "Inicio del sistema",
        13: "Apagado del sistema",
        41: "Sistema reiniciado sin apagado limpio (Kernel-Power)",
        109: "Kernel Power - Apagado inesperado"
    }
    
    for event_id, description in critical_events.items():
        severity = "🔴 CRÍTICO" if event_id in [6008, 41, 109] else "🟡 ALTO"
        print(f"   Event ID {event_id:4d}: {description} [{severity}]")
    
    print()
    
    # 8. Instrucciones de uso
    print("8. 🚀 CÓMO USAR LAS NUEVAS FUNCIONES:")
    print()
    print("   a) Monitoreo automático:")
    print("      - Ejecute: ejecutar_monitor_portable.bat")
    print("      - Seleccione opción 2 o 3 para incluir eventos Windows")
    print()
    print("   b) Configurar eventos específicos:")
    print("      - Edite config.ini, sección [event_monitoring]")
    print("      - Agregue: specific_event_ids = 1074,6008,41")
    print("      - Reinicie el monitor")
    print()
    print("   c) Probar alertas:")
    print("      - python-embedded\\python.exe quadient_sender_simple.py test")
    print()
    
    return True

def search_recent_critical_events():
    """Busca eventos críticos recientes para demostración"""
    critical_events = []
    
    try:
        import win32evtlog
        
        # Buscar en System log
        hand = win32evtlog.OpenEventLog('localhost', 'System')
        
        events = win32evtlog.ReadEventLog(
            hand,
            win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ,
            0
        )
        
        # Eventos críticos que buscamos
        critical_ids = {
            1074: "Apagado/Reinicio iniciado",
            6005: "Sistema iniciado",
            6006: "Sistema apagado",
            6008: "Apagado inesperado",
            41: "Reinicio sin apagado limpio",
            109: "Kernel Power - Apagado inesperado"
        }
        
        count = 0
        for event in events:
            if count >= 50:  # Limitar búsqueda
                break
                
            if event.EventID in critical_ids:
                critical_events.append({
                    'id': event.EventID,
                    'description': critical_ids[event.EventID],
                    'time': event.TimeGenerated,
                    'source': event.SourceName
                })
                
            count += 1
            
        win32evtlog.CloseEventLog(hand)
        
    except Exception as e:
        print(f"   ⚠️ No se pudo acceder a los logs del sistema: {e}")
        
    return critical_events

def show_example_alert():
    """Muestra un ejemplo de alerta de evento crítico"""
    print("9. 📧 EJEMPLO DE ALERTA MEJORADA:")
    print()
    print("   Cuando se detecta un reinicio, recibirá un email como:")
    print()
    print("   📧 Asunto: [ALERTA SEGURIDAD] 🚨 EVENTO CRÍTICO: SISTEMA REINICIO/APAGADO")
    print()
    print("   🚨 EVENTO CRÍTICO DE SISTEMA")
    print("   Severidad: CRÍTICO")
    print("   Categoría: APAGADO/REINICIO")
    print("   Descripción: Apagado/Reinicio iniciado por usuario o aplicación")
    print("   Event ID: 1074")
    print("   Equipo: MI-PC")
    print("   Hora: 2024-01-15 14:30:25")
    print()
    print("   Información de Apagado/Reinicio:")
    print("   • Tipo: Reinicio")
    print("   • Razón: Planned (Maintenance)")
    print("   • Iniciado por usuario: DOMAIN\\usuario")
    print("   • Proceso iniciador: shutdown.exe")
    print()

if __name__ == "__main__":
    # Cambiar al directorio del script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    success = demonstrate_event_monitoring()
    
    if success:
        show_example_alert()
        
        print("=" * 70)
        print("✅ El sistema está listo para detectar eventos críticos del sistema!")
        print()
        print("💡 PRÓXIMOS PASOS:")
        print("   1. Configure eventos específicos en config.ini si es necesario")
        print("   2. Configure las credenciales de email para recibir alertas")
        print("   3. Ejecute el monitor y pruebe con un reinicio del sistema")
        print("=" * 70)
    else:
        print("❌ Hay problemas que deben resolverse antes de usar el sistema.")
        
    input("\nPresione Enter para salir...")