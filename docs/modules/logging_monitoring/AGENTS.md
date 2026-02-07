# Logging & Monitoring Module — Agent Coordination

## Purpose

Codomyrmex Logging Monitoring Module.

## Key Capabilities

- Logging & Monitoring operations and management

## Agent Usage Patterns

```python
from codomyrmex.logging_monitoring import *

# Agent uses logging & monitoring capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/logging_monitoring/](../../../src/codomyrmex/logging_monitoring/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`AuditLogger`** — Specialized logger for recording immutable security and audit events.
- **`JSONFormatter`** — Formatter that outputs log records as JSON objects.
- **`LogContext`** — Context manager for correlation ID and contextual logging.
- **`PerformanceLogger`** — Logger specialized for performance metrics and timing operations.
- **`LogRotationManager`** — Configures and manages rotating file handlers for loggers.
- **`setup_logging()`** — Configure the logging system for the application.
- **`get_logger()`** — Get a logger instance with the specified name.
- **`log_with_context()`** — Log a message with additional context data.
- **`create_correlation_id()`** — Generate a unique correlation ID for request tracing.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k logging_monitoring -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
