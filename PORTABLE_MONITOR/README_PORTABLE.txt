# Monitor Portable de Eventos Windows
## Version Sin Permisos Administrativos

Esta version del monitor funciona completamente portable
y NO requiere permisos administrativos.

### Que monitorea:
- Procesos sospechosos en ejecucion
- Archivos sospechosos en carpetas del usuario
- Alto uso de CPU y memoria
- Cambios en archivos criticos del usuario

### Como usar:
1. Copie toda la carpeta PORTABLE_MONITOR a cualquier ubicacion
2. Ejecute EJECUTAR_MONITOR_PORTABLE.bat
3. El monitor funcionara en segundo plano

### Configuracion:
- Edite config.ini para personalizar la deteccion
- Configure email en la seccion [alerts] para recibir alertas

### Limitaciones:
- No puede acceder a Event Log de Windows (requiere permisos admin)
- Solo monitorea directorios del usuario
- Capacidades limitadas comparado con la version completa

### Logs:
- Los logs se guardan en la carpeta logs\
- Si no puede escribir ahi, usa el directorio del usuario

Esta version es ideal para uso en equipos corporativos
donde no se tienen permisos administrativos.
