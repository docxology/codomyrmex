# Logging Monitoring Core -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Centralized logging configuration, correlation ID threading, and in-memory
log aggregation. Foundation layer consumed by all codomyrmex modules.

## Architecture

Three cooperating subsystems: `logger_config` for Python logging setup,
`correlation` for `contextvars`-based correlation ID propagation across
MCP/event/log boundaries, and `log_aggregator` for in-memory search and
analytics over stored log records.

## Key Classes

### `setup_logging()` (logger_config.py)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `force` | `bool` | `True` | Reconfigure even if already configured |

Environment variables read: `CODOMYRMEX_LOG_LEVEL` (INFO), `CODOMYRMEX_LOG_FILE`, `CODOMYRMEX_LOG_FORMAT`, `CODOMYRMEX_LOG_OUTPUT_TYPE` (TEXT/JSON).

### `LogContext` (logger_config.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `correlation_id: str, additional_context: dict` | -- | Create context with auto-generated or explicit correlation ID |
| `__enter__` | -- | `LogContext` | Set correlation ID for subsequent logs |
| `__exit__` | `exc_type, exc_val, exc_tb` | `None` | Restore previous correlation ID |

### Correlation Functions (correlation.py)

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `new_correlation_id` | -- | `str` | Generate and store `cid-{hex12}` in context |
| `get_correlation_id` | -- | `str` | Retrieve current correlation ID |
| `set_correlation_id` | `cid: str` | `None` | Explicitly set correlation ID |
| `with_correlation` | `cid: str` | `Generator[str]` | Context manager for scoped correlation |
| `enrich_event_data` | `data: dict` | `dict` | Inject correlation ID into event data |
| `create_mcp_correlation_header` | -- | `dict[str, str]` | Generate `x-correlation-id` MCP header |

### `LogAggregator` (log_aggregator.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add` | `record: LogRecord` | `None` | Store a log record |
| `search` | `query: LogQuery` | `list[LogRecord]` | Filter by level, module, time, correlation ID, message substring |
| `stats` | -- | `LogStats` | Aggregate statistics (counts, error rate, top modules) |
| `tail` | `n: int` | `list[LogRecord]` | Most recent n records |

## Dependencies

- **Internal**: `logging_monitoring.audit.audit_logger`, `logging_monitoring.formatters`
- **External**: stdlib (`logging`, `contextvars`, `json`, `os`, `uuid`, `threading`)

## Constraints

- `setup_logging()` is idempotent unless `force=True`.
- Correlation IDs use `contextvars.ContextVar` for async-safe, thread-safe propagation.
- `LogAggregator` stores at most `max_records` (default 100,000) in memory.
- Zero-mock: real log output only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Invalid log level strings fall back to `logging.INFO`.
- File handler creation failure prints a warning but does not raise.
- All errors logged before propagation.
