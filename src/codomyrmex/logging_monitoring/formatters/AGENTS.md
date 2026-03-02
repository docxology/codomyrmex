# Codomyrmex Agents -- src/codomyrmex/logging_monitoring/formatters

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides log formatters for structured output: compact JSON, pretty-printed
JSON for development, redacted JSON for production (auto-redacts sensitive
fields like passwords and tokens), and a full structured formatter with
configurable fields, correlation IDs, and stacktrace capture.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `json_formatter.py` | `JSONFormatter` | Compact JSON log formatter with include/exclude field filtering |
| `json_formatter.py` | `PrettyJSONFormatter` | Indented JSON formatter for development and debugging |
| `json_formatter.py` | `RedactedJSONFormatter` | Auto-redacts fields matching sensitive patterns (password, token, api_key, etc.) |
| `structured_formatter.py` | `StructuredFormatter` | JSON-lines formatter with configurable fields, static fields, correlation IDs, and stacktrace |
| `structured_formatter.py` | `FormatterConfig` | Configuration dataclass for StructuredFormatter (timestamp, level, module, stacktrace toggles) |
| `structured_formatter.py` | `LogLevel` | Enum for standard log levels (DEBUG through CRITICAL) |
| `structured_formatter.py` | `LogContext` | Contextual metadata (correlation_id, module, function, extra) |
| `structured_formatter.py` | `StructuredLogEntry` | Single structured log entry with level, message, context, error, and fields |

## Operating Contracts

- `JSONFormatter` extends `logging.Formatter` and is compatible with Python's standard logging.
- `RedactedJSONFormatter` recursively scans all field names against `_SENSITIVE_PATTERNS` regex.
- `StructuredFormatter` is a standalone class (not a `logging.Formatter` subclass) -- it formats `StructuredLogEntry` objects.
- Messages exceeding `max_message_length` are truncated with `...` suffix.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: stdlib `logging`, `json`, `re`, `time`, `traceback`
- **Used by**: `logging_monitoring.core.logger_config`, `logging_monitoring.audit.audit_logger`, all modules via `setup_logging()`

## Navigation

- **Parent**: [logging_monitoring](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
