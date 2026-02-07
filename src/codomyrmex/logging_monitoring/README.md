# Logging Monitoring Module

**Version**: v0.1.0 | **Status**: Active

Centralized logging with configurable levels, formats, and outputs.

## Key Exports

### Classes
- **`AuditLogger`** — Specialized logger for recording immutable security and audit events.
- **`JSONFormatter`** — Formatter that outputs log records as JSON objects.
- **`LogContext`** — Context manager for correlation ID and contextual logging.
- **`PerformanceLogger`** — Logger specialized for performance metrics and timing operations.
- **`LogRotationManager`** — Configures and manages rotating file handlers for loggers.

### Functions
- **`setup_logging()`** — Configure the logging system for the application.
- **`get_logger()`** — Get a logger instance with the specified name.
- **`log_with_context()`** — Log a message with additional context data.
- **`create_correlation_id()`** — Generate a unique correlation ID for request tracing.

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


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k logging_monitoring -v
```


## Documentation

- [Module Documentation](../../../docs/modules/logging_monitoring/README.md)
- [Agent Guide](../../../docs/modules/logging_monitoring/AGENTS.md)
- [Specification](../../../docs/modules/logging_monitoring/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
