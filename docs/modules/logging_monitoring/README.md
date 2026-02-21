# Logging & Monitoring Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Structured logging, metric collection, and system monitoring with pluggable backends.

## Key Features

- **AuditLogger** — Specialized logger for recording immutable security and audit events.
- **JSONFormatter** — Formatter that outputs log records as JSON objects.
- **LogContext** — Context manager for correlation ID and contextual logging.
- **PerformanceLogger** — Logger specialized for performance metrics and timing operations.
- **LogRotationManager** — Configures and manages rotating file handlers for loggers.
- `setup_logging()` — Configure the logging system for the application.
- `get_logger()` — Get a logger instance with the specified name.
- `log_with_context()` — Log a message with additional context data.
- `create_correlation_id()` — Generate a unique correlation ID for request tracing.

## Quick Start

```python
from codomyrmex.logging_monitoring import AuditLogger, JSONFormatter, LogContext

instance = AuditLogger()
```

## Source Files

- `audit.py`
- `json_formatter.py`
- `logger_config.py`
- `rotation.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |
| `tutorials/` | Tutorials |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k logging_monitoring -v
```

## Navigation

- **Source**: [src/codomyrmex/logging_monitoring/](../../../src/codomyrmex/logging_monitoring/)
- **Parent**: [Modules](../README.md)
