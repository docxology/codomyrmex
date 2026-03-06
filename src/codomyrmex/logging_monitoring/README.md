# Logging & Monitoring Module

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

Centralized logging with configurable levels, formats, and outputs.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **ALL PHASES** | Structured logging of all Algorithm actions and tool invocations | `logging_format_structured` |
| **LEARN** | Archive structured logs for retrospective analysis | `logging_format_structured` |
| **VERIFY** | Validate log output format and completeness | `logging_format_structured` |

Every PAI Algorithm phase emits structured logs via this module. `logging_format_structured` is called by Engineer agents throughout BUILD and EXECUTE; all phase transition logs are archived for LEARN phase retrospectives. The monitoring integration forwards alerts when anomalies are detected.

## Key Exports

The following are exported from the top-level `codomyrmex.logging_monitoring`:

### Core API
- **`setup_logging()`** — Configure the logging system for the application.
- **`get_logger(name)`** — Get a logger instance with the specified name.
- **`LogContext`** — Context manager for correlation ID and contextual logging.
- **`log_with_context()`** — Log a message with additional context data.
- **`JSONFormatter`** — Formatter that outputs log records as JSON objects.

### Correlation & Tracing
- **`new_correlation_id()`**, **`get_correlation_id()`**, **`set_correlation_id()`** — Manage the active correlation ID.
- **`with_correlation()`** — Context manager for simple correlation ID propagation.
- **`CorrelationFilter`** — Logging filter that injects correlation IDs into records.

### Specialized Loggers (importable from subpackages)
- **`AuditLogger`** — Specialized logger for security and audit events (in `.audit`).
- **`PerformanceLogger`** — Logger for performance metrics and timing (in `.handlers`).
- **`LogRotationManager`** — Manages rotating file handlers (in `.handlers`).
- **`StructuredFormatter`** — High-performance JSON-lines formatter (in `.formatters`).

## Quick Start

```python
from codomyrmex.logging_monitoring import setup_logging, get_logger

# Initialize logging (once at startup)
setup_logging()

# Get module-specific logger
logger = get_logger(__name__)

# Log at different levels
logger.info("Operation completed successfully")
```

## Usage Examples

### Structured Logging and Context

```python
from codomyrmex.logging_monitoring import (
    setup_logging, get_logger, LogContext, log_with_context, with_correlation
)

setup_logging()
logger = get_logger(__name__)

# Using LogContext for automatic correlation ID and extra context
with LogContext(correlation_id="req-123", additional_context={"user": "alice"}) as ctx:
    logger.info("Processing request")  # Automatically includes correlation_id and user

# Using log_with_context for one-off structured logs
log_with_context("info", "Task started", {"task_id": 42, "priority": "high"})

# Using with_correlation for simple ID propagation
with with_correlation("trace-789") as cid:
    logger.info(f"Trace ID {cid} is active")
```

### Audit Logging

```python
from codomyrmex.logging_monitoring.audit import AuditLogger

audit = AuditLogger()
audit.log_event(
    event_type="sensitive_access",
    user_id="user_99",
    status="success",
    severity="info",
    category="access",
    details={"resource": "vault_01"}
)

# Query recent failures
failures = audit.failures(limit=10)
```

### Performance Monitoring

```python
from codomyrmex.logging_monitoring.handlers import PerformanceLogger

perf = PerformanceLogger("database_service")

# Time a code block
with perf.time_operation("complex_query", context={"table": "users"}):
    # ... expensive database operation ...
    pass

# Log custom metrics
perf.log_metric("cache_hit_ratio", 0.98, unit="percent")
```

### Log Rotation and Management

```python
from codomyrmex.logging_monitoring.handlers import LogRotationManager
import logging

mgr = LogRotationManager(log_dir="./logs")
mgr.attach_rotating_handler(
    logger_name="app.api",
    filename="api.log",
    max_bytes=10 * 1024 * 1024, # 10MB
    backup_count=5
)

# Check disk usage
usage = mgr.disk_usage()
print(f"Total log size: {usage['total_mb']} MB")
```

### Advanced Formatting

```python
import logging
from codomyrmex.logging_monitoring import JSONFormatter
from codomyrmex.logging_monitoring.formatters import RedactedJSONFormatter

# Redact sensitive information
handler = logging.StreamHandler()
handler.setFormatter(RedactedJSONFormatter(patterns=["credit_card", "ssn"]))

logger = logging.getLogger("secure_logger")
logger.addHandler(handler)
logger.info("User data", extra={"credit_card": "1234-5678-9012-3456"})
# Output will have: "credit_card": "[REDACTED]"
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
