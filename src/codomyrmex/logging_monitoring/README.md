# Logging Monitoring Module

**Version**: v0.1.0 | **Status**: Active

Centralized logging with configurable levels, formats, and outputs.

## Quick Start

```python
from codomyrmex.logging_monitoring import setup_logging, get_logger

# Initialize logging (once at startup)
setup_logging()

# Get module-specific logger
logger = get_logger(__name__)

# Log at different levels
logger.debug("Detailed debugging information")
logger.info("Operation completed successfully")
logger.warning("Something unexpected happened")
logger.error("Operation failed", exc_info=True)
logger.critical("System is in critical state")
```

## Configuration

Set via environment variables or `.env` file:

| Variable | Description | Example |
|----------|-------------|---------|
| `CODOMYRMEX_LOG_LEVEL` | Minimum log level | `DEBUG`, `INFO`, `WARNING` |
| `CODOMYRMEX_LOG_FILE` | Log file path | `/var/log/codomyrmex.log` |
| `CODOMYRMEX_LOG_FORMAT` | Format string or preset | `DETAILED` |

## Usage Pattern

```python
# In main.py
from codomyrmex.logging_monitoring import setup_logging
setup_logging()

# In any other module
from codomyrmex.logging_monitoring import get_logger
logger = get_logger(__name__)
```

## Exports

| Function | Description |
|----------|-------------|
| `setup_logging()` | Initialize logging system |
| `get_logger(name)` | Get a named logger instance |

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
