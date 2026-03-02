# Formatters -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Log formatting subsystem providing JSON, pretty JSON, redacted JSON, and
structured JSON-lines formatters for production log pipelines (ELK, Loki,
Datadog) and development output.

## Architecture

Two formatter families: `json_formatter.py` provides three `logging.Formatter`
subclasses compatible with Python's logging framework. `structured_formatter.py`
provides a standalone `StructuredFormatter` that formats custom `StructuredLogEntry`
dataclasses into JSON-lines.

## Key Classes

### `JSONFormatter` (json_formatter.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `datefmt, include_fields, exclude_fields` | -- | Configure field filtering |
| `format` | `record: logging.LogRecord` | `str` | Compact JSON string |

### `PrettyJSONFormatter` (json_formatter.py)

Extends `JSONFormatter` with configurable `indent` (default 2).

### `RedactedJSONFormatter` (json_formatter.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `patterns: list[str], replacement: str` | -- | Additional regex patterns and replacement text |
| `format` | `record: logging.LogRecord` | `str` | JSON with sensitive fields replaced by `[REDACTED]` |

Default patterns: `password`, `secret`, `token`, `api_key`, `auth`, `credential`, `ssn`, `credit_card`.

### `StructuredFormatter` (structured_formatter.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `format` | `entry: StructuredLogEntry` | `str` | Single JSON line (or indented if `pretty_print`) |
| `format_batch` | `entries: list[StructuredLogEntry]` | `str` | Newline-delimited JSON strings |

### `FormatterConfig` (structured_formatter.py)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `include_timestamp` | `bool` | `True` | Include ISO-8601 timestamp |
| `include_level` | `bool` | `True` | Include log level |
| `include_module` | `bool` | `True` | Include module/function fields |
| `include_correlation_id` | `bool` | `True` | Include correlation ID |
| `include_stacktrace` | `bool` | `True` | Include stacktrace on errors |
| `pretty_print` | `bool` | `False` | Indent JSON output |
| `max_message_length` | `int` | `0` | Truncate messages (0=no limit) |
| `static_fields` | `dict` | `{}` | Fields in every log line (e.g., service, env) |

## Dependencies

- **Internal**: None (standalone formatters)
- **External**: stdlib (`logging`, `json`, `re`, `time`, `traceback`, `dataclasses`, `enum`)

## Constraints

- `RedactedJSONFormatter` recursively redacts nested dicts but not lists of dicts.
- `StructuredFormatter` tracks line count via `lines_formatted` property.
- Zero-mock: real formatting only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `JSONFormatter.format()` uses `default=str` to handle non-serializable values.
- Exception info is included in output when `record.exc_info` is set.
- All errors logged before propagation.
