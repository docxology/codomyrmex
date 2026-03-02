# Events Handlers — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides the receive side of the event system: `EventListener` for manual handler registration with one-shot support, `AutoEventListener` for decorator-driven auto-registration, and `EventLogger` for persistent event history with statistics, filtering, and export.

## Architecture

Observer pattern with two registration modes: explicit (`EventListener.on()`) and declarative (`@event_handler` decorator + `AutoEventListener.register_handlers()`). `EventLogger` subscribes to all events via wildcard pattern `"*"` and maintains a bounded in-memory history with thread-safe access.

## Key Classes

### `EventListener`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `listener_id: str`, `event_bus: EventBus \| None` | `None` | Initialize with ID and optional bus |
| `on` | `event_types`, `handler`, `handler_name`, `filter_func`, `priority` | `str` | Register handler; returns handler name |
| `once` | (same as `on`) | `str` | Register one-shot handler (auto-unsubscribes after first call) |
| `off` | `handler_name: str` | `bool` | Unsubscribe a handler by name |
| `listen_to_analysis_events` | `handler` | `list[str]` | Subscribe to ANALYSIS_START/PROGRESS/COMPLETE/ERROR |
| `listen_to_build_events` | `handler` | `list[str]` | Subscribe to BUILD_START/PROGRESS/COMPLETE/ERROR |

### `AutoEventListener`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register_handlers` | `obj: Any` | `None` | Scan object for `@event_handler`-decorated methods and auto-register them |

### `EventLogger`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `max_entries: int = 10000`, `event_bus: EventBus \| None` | `None` | Initialize bounded log and subscribe to all events |
| `log_event` | `event: Event`, `handler_count: int`, `processing_time: float` | `None` | Record an event entry |
| `get_event_statistics` | — | `dict` | Return total events, per-type counts, error counts |
| `get_events` | `event_type: str \| None`, `start_time`, `end_time` | `list[EventLogEntry]` | Filter event history |
| `get_events_by_type` | `event_type: EventType \| str` | `list[EventLogEntry]` | Filter by specific type |
| `get_error_events` | — | `list[EventLogEntry]` | Return entries where type contains "error" |
| `get_recent_events` | `limit: int = 50` | `list[EventLogEntry]` | Return last N entries |
| `get_performance_report` | — | `dict` | Total and average processing times by event type |
| `export_logs` | `path: str`, `format: str = "json"` | `None` | Export to JSON or CSV file |
| `clear` | — | `None` | Reset all entries and counters |

## Dependencies

- **Internal**: `events.core.event_bus`, `events.core.event_schema`
- **External**: Standard library only (`json`, `threading`, `collections`, `datetime`)

## Constraints

- `EventLogger.entries` uses `deque(maxlen=max_entries)`; oldest entries are automatically evicted when capacity is reached.
- `EventLogger` is thread-safe via `threading.Lock` for all read and write operations.
- `once()` handlers use `try/finally` to guarantee unsubscription even if the handler raises.
- `@event_handler` decorator stores metadata as function attributes (`_event_types`, `_event_filter`, `_event_priority`, `_is_event_handler`).
- `AutoEventListener.register_handlers` uses `attr.__get__(obj, obj.__class__)` for proper method binding.
- The global `EventLogger` singleton is lazily initialized via `get_event_logger()`.

## Error Handling

- Handler exceptions in `EventListener` propagate to the event bus (which catches and logs them).
- `export_logs` may raise `OSError` or `IOError` for filesystem errors -- these are not caught internally.
- `EventLogEntry.to_dict()` safely handles both enum and non-enum values for event_type and priority via `hasattr` checks.
