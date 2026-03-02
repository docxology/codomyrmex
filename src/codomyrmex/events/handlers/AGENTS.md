# Codomyrmex Agents — src/codomyrmex/events/handlers

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides event listener and logging components for the receive side of the event system: manual and automatic handler registration, one-shot subscriptions, event history with statistics, performance reporting, and log export.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `event_listener.py` | `EventListener` | Manages named handler subscriptions with `on()`, `once()` (auto-unsubscribe), `off()`, and convenience methods for analysis/build event groups |
| `event_listener.py` | `AutoEventListener` | Extends `EventListener`; scans an object for methods decorated with `@event_handler` and auto-registers them |
| `event_listener.py` | `event_handler` | Decorator marking methods as event handlers with `_event_types`, `_event_filter`, and `_event_priority` attributes |
| `event_listener.py` | `create_listener()` / `create_auto_listener()` | Factory functions for `EventListener` and `AutoEventListener` |
| `event_logger.py` | `EventLogEntry` | Wraps an `Event` with timestamp, handler count, and processing time; provides `to_dict()` for serialization |
| `event_logger.py` | `EventLogger` | Thread-safe event logger subscribing to all events (`"*"`); maintains a bounded `deque` of entries (default 10,000), event/error count dicts, and processing time lists |
| `event_logger.py` | `get_event_logger()` | Module-level singleton accessor for the global `EventLogger` |
| `event_logger.py` | `get_event_stats()` / `get_recent_events()` / `generate_performance_report()` / `export_event_logs()` | Convenience functions delegating to the singleton |

## Operating Contracts

- `EventListener.once()` wraps the handler in a one-time wrapper that calls `off()` after the first invocation (via `try/finally`).
- `AutoEventListener.register_handlers()` uses `getattr` introspection to find methods with `_is_event_handler = True` and binds them correctly.
- `EventLogger` subscribes to pattern `"*"` (all events) on initialization and is thread-safe via `threading.Lock`.
- `EventLogger.entries` is a bounded `deque(maxlen=max_entries)` -- oldest entries are evicted automatically.
- `export_logs()` supports `json` and `csv` formats; writes directly to the filesystem.
- `EventListener.enabled` flag prevents new subscriptions when set to `False`.

## Integration Points

- **Depends on**: `events.core.event_bus` (`EventBus`, `get_event_bus`, `subscribe_to_events`, `unsubscribe_from_events`), `events.core.event_schema` (`Event`, `EventType`), `codomyrmex.logging_monitoring`
- **Used by**: Monitoring dashboards, debugging tools, and any module that needs to react to or record events

## Navigation

- **Parent**: [events](../README.md)
- **Root**: [Codomyrmex](../../../../../README.md)
