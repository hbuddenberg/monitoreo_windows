# Mejoras en el Sistema de Monitoreo de Eventos Windows

Se han realizado mejoras significativas y **nuevas funcionalidades críticas** al sistema de monitoreo, incluyendo detección avanzada de eventos de reinicio/apagado y búsqueda específica de Event IDs.

## 🆕 NUEVAS FUNCIONALIDADES CRÍTICAS (v2.0)

### 🚨 Detección de Eventos de Reinicio/Apagado del Sistema
- **Monitoreo automático** de eventos críticos de sistema
- **Detección inmediata** cuando el sistema va a reiniciar o apagar
- **Información detallada** sobre quién/qué inició el reinicio
- **Alertas críticas** para fallos inesperados del sistema

### 🎯 Búsqueda Específica de Event IDs
- **Configuración de eventos prioritarios** - busca Event IDs específicos primero
- **Búsqueda inteligente** - si no encuentra eventos específicos, busca en todos
- **Monitoreo flexible** - configure exactamente qué eventos necesita detectar

### 📧 Sistema de Alertas Mejorado
- **Emails detallados** con información completa del evento
- **Categorización automática** (APAGADO/REINICIO, FALLO CRÍTICO, etc.)
- **Diferentes niveles de severidad** (LOW, MEDIUM, HIGH, CRITICAL)
- **Templates específicos** para cada tipo de evento

## Eventos Críticos Monitoreados Automáticamente

| Event ID | Descripción | Severidad | Categoría |
|----------|-------------|-----------|-----------|
| **1074** | Apagado/Reinicio iniciado por usuario o aplicación | HIGH | APAGADO/REINICIO |
| **6005** | Event Log Service iniciado (arranque del sistema) | HIGH | ARRANQUE SISTEMA |
| **6006** | Event Log Service detenido (apagado del sistema) | HIGH | APAGADO/REINICIO |
| **6008** | Apagado inesperado del sistema | **CRITICAL** | FALLO CRÍTICO |
| **1076** | Apagado iniciado pero cancelado | HIGH | APAGADO/REINICIO |
| **6013** | Tiempo de actividad del sistema | MEDIUM | INFORMACIÓN SISTEMA |
| **12** | Inicio del sistema | HIGH | ARRANQUE SISTEMA |
| **13** | Apagado del sistema | HIGH | APAGADO/REINICIO |
| **41** | Sistema reiniciado sin apagado limpio (Kernel-Power) | **CRITICAL** | FALLO CRÍTICO |
| **109** | Kernel Power - Apagado inesperado | **CRITICAL** | FALLO CRÍTICO |

## Configuración de Búsqueda Específica

Para monitorear Event IDs específicos, configure en `config.ini`:

```ini
[event_monitoring]
# Para buscar solo eventos de reinicio críticos:
specific_event_ids = 1074,6008,41

# Para buscar eventos de autenticación:
specific_event_ids = 4625,4624

# Para buscar múltiples eventos críticos:
specific_event_ids = 1074,4625,7034,6008

# Si no se encuentran eventos específicos, buscar en todos:
search_all_if_not_found = true
```

## Cambios realizados

1. **Detección Avanzada de Eventos**: 
   - Monitor automático de eventos críticos de sistema
   - Análisis detallado de eventos de reinicio/apagado
   - Extracción de información sobre quién inició el reinicio

2. **Búsqueda Inteligente**:
   - Priorización de Event IDs específicos configurados
   - Búsqueda en todos los eventos si no se encuentran específicos
   - Límites de procesamiento para evitar sobrecarga del sistema

3. **Nuevos Scripts Mejorados**:
   - `INSTALAR_PORTABLE.bat`: Configura automáticamente el entorno portable
   - `ejecutar_monitor_portable.bat`: Menú mejorado con opciones de monitoreo
   - `demo_eventos_criticos.py`: Demostración de nuevas funcionalidades
   - `test_sistema_completo.py`: Pruebas actualizadas

4. **Sistema de Alertas Avanzado**:
   - Templates específicos para eventos críticos
   - Emails con información detallada de shutdown/reboot
   - Categorización automática de eventos
   - Diferentes niveles de severidad

5. **Documentación Actualizada**:
   - `GUIA_PORTABLE.md`: Instrucciones detalladas actualizadas
   - Ejemplos de configuración para eventos específicos

## Cómo usar la versión portable

1. Ejecute `INSTALAR_PORTABLE.bat` para configurar el entorno
2. Siga las instrucciones en pantalla
3. Una vez instalado, puede ejecutarlo manualmente o configurar el inicio automático

Para más detalles, consulte el archivo `GUIA_PORTABLE.md`.

## Ventajas de la versión portable

- Funciona en cualquier equipo Windows, independientemente de si tiene Python instalado
- No requiere permisos de administrador para la mayoría de las funciones
- Fácil de distribuir como una solución completa
- El entorno Python está aislado y no interfiere con otras instalaciones

## Requisitos mínimos

- Sistema operativo: Windows 7 o superior
- Espacio en disco: ~50MB para Python embebido y dependencias
- Memoria RAM: 50MB mínimo

## Funcionamiento técnico

La versión portable descarga una versión embebida de Python 3.10 e instala las dependencias necesarias dentro del entorno portable. Todos los scripts están configurados para usar este Python embebido en lugar de buscar una instalación del sistema.

---

*Nota: La versión original (no portable) sigue funcionando como antes para equipos que ya tienen Python instalado.*
