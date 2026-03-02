# Codomyrmex Agents — src/codomyrmex/events/emitters

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides synchronous and asynchronous event emission components with correlation tracking, batch operations, operation lifecycle management (start/update/end), and convenience functions for error, metric, and alert events.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `emitter.py` | `AsyncEventEmitter` | Lightweight async emitter with `emit()` and `emit_later()` (delayed emission via `asyncio.sleep`) |
| `event_emitter.py` | `EventEmitter` | Full-featured emitter with sync/async emit, batch emit, operation lifecycle (`start_operation` / `update_operation` / `end_operation`), error/metric/alert shortcuts, enable/disable toggle, correlation context, and default metadata |
| `event_emitter.py` | `EventOperationContext` | Context manager wrapping `EventEmitter.start_operation()` / `end_operation()` with automatic duration tracking and success/failure detection |
| `event_emitter.py` | `create_emitter()` | Factory function returning an `EventEmitter` for a given source identifier |
| `event_emitter.py` | `emit_event()` | One-shot convenience function that creates a temporary emitter and publishes a single event |

## Operating Contracts

- `EventEmitter` respects its `enabled` flag; all emit methods are no-ops when disabled.
- `emit()` catches `RuntimeError` and `AttributeError` from the bus and logs them without propagating.
- `start_operation()` generates a UUID correlation ID and sets it as the default for subsequent events until `end_operation()` clears it.
- `end_operation()` sets priority=2 (high) for failed operations.
- `EventOperationContext.__exit__` automatically calls `end_operation` with `success=False` if an exception occurred.
- Batch emit (`emit_batch_async`) uses `asyncio.gather` with `return_exceptions=True` to prevent one failure from blocking others.

## Integration Points

- **Depends on**: `events.core.event_bus` (`EventBus`, `get_event_bus`), `events.core.event_schema` (`Event`, `EventType`), `codomyrmex.logging_monitoring`
- **Used by**: Any module that needs to publish events; typically instantiated via `create_emitter("module_name")`

## Navigation

- **Parent**: [events](../README.md)
- **Root**: [Codomyrmex](../../../../../README.md)
