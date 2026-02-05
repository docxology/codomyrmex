# logging_monitoring

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Foundation-layer module providing centralized logging infrastructure for the entire Codomyrmex platform. Delivers consistent log formatting, configurable log levels and output destinations (console, file), structured JSON logging for machine parsing, immutable audit logging for security events, and automated log rotation for disk space management. All other modules depend on this module for their logging needs.

## Key Exports

- **`setup_logging()`** -- Initialize the logging system. Call once at application startup to configure log level, format, and output destinations from environment variables (`CODOMYRMEX_LOG_LEVEL`, `CODOMYRMEX_LOG_FILE`, `CODOMYRMEX_LOG_FORMAT`)
- **`get_logger(name)`** -- Return a configured logger instance for the given module name. Use `get_logger(__name__)` in any module to obtain a logger that inherits the centralized configuration

## Configuration

Set these environment variables (or in a `.env` file):

| Variable | Purpose | Example |
|---|---|---|
| `CODOMYRMEX_LOG_LEVEL` | Minimum log level | `DEBUG`, `INFO`, `WARNING` |
| `CODOMYRMEX_LOG_FILE` | File output path | `/var/log/codomyrmex.log` |
| `CODOMYRMEX_LOG_FORMAT` | Format string or preset | `DETAILED` or a custom `%` format |

## Directory Contents

- `logger_config.py` -- Core logging configuration: `setup_logging()` and `get_logger()` implementations
- `json_formatter.py` -- `JSONFormatter` class that outputs log records as structured JSON objects with timestamp, level, module, and exception data
- `audit.py` -- `AuditLogger` class for recording immutable security and compliance events with structured event type, user ID, status, and details
- `rotation.py` -- `LogRotationManager` class for attaching size-based rotating file handlers to loggers with configurable max bytes and backup count

## Navigation

- **Full Documentation**: [docs/modules/logging_monitoring/](../../../docs/modules/logging_monitoring/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
