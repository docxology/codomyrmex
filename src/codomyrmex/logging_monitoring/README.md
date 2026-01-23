# Logging Monitoring Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Logging Monitoring module provides centralized logging facilities for the Codomyrmex project. It enables consistent log formatting, configurable log levels, and multiple output targets (console, file, JSON) across all modules. This is a **Foundation Layer** module that all other modules depend on.

## Key Features

- **Centralized Configuration**: Single point of control for all logging settings
- **Multiple Formats**: Text, JSON, and detailed structured logging
- **Flexible Output**: Console, file, and rotating file handlers
- **Session Correlation**: Track related log entries across operations
- **Environment-Based Config**: Configure via `.env` file or environment variables

## Quick Start

### 1. Setup Logging (Application Entry Point)

```python
from codomyrmex.logging_monitoring import setup_logging

# Initialize logging system (call once at startup)
setup_logging()
```

### 2. Get Logger in Any Module

```python
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

logger.info("Operation started")
logger.debug("Processing data: %s", data)
logger.warning("Resource usage high")
logger.error("Operation failed", exc_info=True)
```

## Configuration

### Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `CODOMYRMEX_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `CODOMYRMEX_LOG_FILE` | None | Path to log file (optional) |
| `CODOMYRMEX_LOG_FORMAT` | `standard` | Format type (standard, detailed, json) |

### Example `.env` Configuration

```bash
CODOMYRMEX_LOG_LEVEL=DEBUG
CODOMYRMEX_LOG_FILE=/var/log/codomyrmex/app.log
CODOMYRMEX_LOG_FORMAT=json
```

## Directory Contents

| File | Purpose |
| :--- | :--- |
| `logger_config.py` | Primary configuration and logger factory |
| `json_formatter.py` | JSON output formatter |
| `audit.py` | Domain-specific audit logging |
| `rotation.py` | Log file rotation management |
| `__init__.py` | Public API exports |

## API Reference

### `setup_logging(config: dict = None) -> None`

Initialize the logging system. Call once at application startup.

```python
setup_logging({
    "level": "DEBUG",
    "file": "/path/to/logs/app.log",
    "format": "json"
})
```

### `get_logger(name: str) -> Logger`

Get a configured logger instance for a module.

```python
logger = get_logger(__name__)
logger.info("Message with %s", "parameters")
```

## Log Formats

### Standard Format
```
2026-01-22 10:30:45 - module_name - INFO - Log message here
```

### Detailed Format
```
2026-01-22 10:30:45.123 | INFO     | module_name:function:42 - Log message here
```

### JSON Format
```json
{"timestamp": "2026-01-22T10:30:45.123Z", "level": "INFO", "module": "module_name", "message": "Log message here"}
```

## Integration

As a Foundation Layer module, logging_monitoring is used by all other Codomyrmex modules:

```python
# In any module
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)
```

## Related Documentation

- [API Specification](API_SPECIFICATION.md)
- [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md)
- [Usage Examples](USAGE_EXAMPLES.md)
- [Security Considerations](SECURITY.md)

## Signposting

### Navigation

- **Self**: [README.md](README.md)
- **Parent**: [src/codomyrmex](../README.md)
- **Siblings**: [environment_setup](../environment_setup/README.md), [terminal_interface](../terminal_interface/README.md)

### Related Files

- [AGENTS.md](AGENTS.md) - Agent coordination for this module
- [SPEC.md](SPEC.md) - Functional specification
- [CHANGELOG.md](CHANGELOG.md) - Version history
