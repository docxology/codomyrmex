# Handlers -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Specialized log handlers for event bridging, WebSocket streaming, rotating
file output, and performance timing. Extends Python's logging framework
with production-grade capabilities.

## Architecture

Four independent handler implementations. `EventLoggingBridge` bridges
the `EventBus` to structured logs. `WebSocketLogHandler` extends
`logging.Handler` with async queue broadcasting. `LogRotationManager`
wraps `RotatingFileHandler` with lifecycle management. `PerformanceLogger`
provides timing utilities.

## Key Classes

### `EventLoggingBridge` (event_bridge.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `event_bus, event_types, logger_name, log_level` | -- | Configure bridge with optional event type filter |
| `start` | -- | `None` | Subscribe to EventBus events |
| `stop` | -- | `None` | Unsubscribe all handlers |
| `events_captured` | -- (property) | `list[dict]` | List of captured event dicts |
| `capture_count` | -- (property) | `int` | Number of events captured |

### `WebSocketLogHandler` (ws_handler.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `emit` | `record: logging.LogRecord` | `None` | Format and enqueue record for broadcast |
| `add_client` | -- | `asyncio.Queue` | Register a WebSocket client, return its queue |
| `remove_client` | `client_queue` | `None` | Unregister a client |
| `stream` | -- | `AsyncGenerator` | Async generator yielding log entry dicts |
| `client_count` | -- (property) | `int` | Number of active WebSocket clients |
| `dropped_count` | -- (property) | `int` | Number of entries dropped due to backpressure |

### `LogRotationManager` (rotation.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `attach_rotating_handler` | `logger_name, filename, max_bytes, backup_count, level` | `RotatingFileHandler` | Attach a rotating handler to a logger |
| `remove_handler` | `logger_name, filename` | `bool` | Remove a previously attached handler |
| `disk_usage` | -- | `dict` | Total bytes, file count, largest file |
| `cleanup_old_logs` | `max_age_days: float` | `int` | Remove files older than threshold, return count |

### `PerformanceLogger` (performance.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `start_timer` | `operation: str, context: dict` | `None` | Begin timing an operation |
| `end_timer` | `operation: str, context: dict` | `float` | End timing, return duration in seconds |
| `time_operation` | `operation: str, context: dict` | `Iterator` | Context manager for block timing |
| `log_metric` | `name, value, unit, context` | `None` | Log a named performance metric |

## Dependencies

- **Internal**: `events.core.event_bus`, `events.core.event_schema`
- **External**: stdlib (`logging`, `asyncio`, `os`, `time`, `pathlib`, `logging.handlers`)

## Constraints

- `WebSocketLogHandler` uses `asyncio.Queue` with `maxsize` -- not usable in synchronous-only code.
- `LogRotationManager` defaults: 10 MB max file size, 5 backup files.
- Zero-mock: real handlers only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `WebSocketLogHandler.emit()` delegates to `handleError()` on exception.
- `LogRotationManager.disk_usage()` returns zero values if log directory does not exist.
- `PerformanceLogger.end_timer()` returns 0.0 if operation was never started.
- All errors logged before propagation.
