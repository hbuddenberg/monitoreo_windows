# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Windows event monitoring system designed for security monitoring and threat detection. The system comes in multiple variants:

- **Full System Monitor** (`windows_event_monitor.py`): Complete monitoring with Windows Event Log access (requires admin privileges)
- **Ultra Portable Monitor** (`monitor_ultra_portable.py`): Minimal version using only Python standard library (no admin required)
- **Portable Monitor** (`PORTABLE_MONITOR/portable_monitor.py`): Standalone version with embedded Python runtime

## Architecture

### Core Components

- **Event Monitoring**: Windows Event Log parsing and analysis
- **Process Monitoring**: Detection of suspicious processes and resource usage
- **File Monitoring**: Filesystem change detection and malicious file analysis
- **Code Analysis** (`code_analyzer.py`): Static analysis for malicious patterns, entropy calculation
- **Alert System** (`quadient_sender_simple.py`): Multi-channel notifications (email, webhook, Windows notifications)

### Configuration

All system behavior is controlled via `config.ini` with sections:
- `[event_monitoring]`: Event IDs, sources, suspicious keywords
- `[process_monitoring]`: Process detection rules, resource thresholds
- `[file_monitoring]`: Directories, file patterns, analysis limits
- `[alerts]`: Notification methods and recipients
- `[thresholds]`: Alert sensitivity settings

## Development Commands

### Dependencies Installation
```bash
pip install -r requirements.txt
```

### Running the Monitors
```bash
# Full system monitor (requires admin)
python windows_event_monitor.py

# Ultra portable monitor (no admin required)
python monitor_ultra_portable.py

# Portable version
cd PORTABLE_MONITOR
EJECUTAR_MONITOR_PORTABLE.bat
```

### Testing
```bash
# Test complete system functionality
python test_sistema_completo.py

# Test alert system
python quadient_sender_simple.py test

# Verify portable installation
PORTABLE_MONITOR/VERIFICAR_PORTABLE.bat
```

### Portable Distribution
```bash
# Create portable distribution
CREAR_PORTABLE_COMPLETO.bat

# Install portable version
INSTALAR_PORTABLE.bat
```

## Key Design Patterns

### Multi-Threading Architecture
- Separate threads for event monitoring, process monitoring, and file monitoring
- Thread-safe logging and alert management
- Graceful shutdown handling with threading events

### Plugin-Style Monitoring
- Each monitor type (Event/Process/File) is a separate class
- Common interface for start/stop operations
- Configurable enable/disable per monitor type

### Alert Deduplication
- Cache-based system to prevent alert spam
- Configurable cooldown periods per alert type
- Severity-based filtering

### Defensive Security Focus
This system is designed for **defensive security only**. It detects:
- Malicious processes and files
- Suspicious system events
- Unauthorized system changes
- Resource abuse patterns

Do not modify the detection patterns to bypass security systems or create offensive tools.

## Important Files

- `config.ini`: Main configuration file - modify this to change monitoring behavior
- `logs/`: All system logs are stored here
- `GUIA_PORTABLE.md`: Comprehensive installation and usage guide
- `requirements.txt`: Python dependencies for the full system