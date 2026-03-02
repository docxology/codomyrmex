# Events Emitters — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides event emission abstractions at two levels: a lightweight `AsyncEventEmitter` for simple async publishing, and a full-featured `EventEmitter` with correlation tracking, operation lifecycle management, batch operations, and typed convenience methods for errors, metrics, and alerts.

## Architecture

Facade pattern over `EventBus`. Emitters encapsulate a source identifier and delegate to the global (or injected) event bus. `EventOperationContext` implements the context manager protocol for structured start/end event pairs with automatic timing and error detection.

## Key Classes

### `AsyncEventEmitter`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `bus: Any \| None` | `None` | Initialize with optional event bus (defaults to global) |
| `emit` | `event_type: EventType`, `payload: Any`, `priority: int = 0` | `None` | Async: emit a single event |
| `emit_later` | `event_type: EventType`, `payload: Any`, `delay: float` | `None` | Schedule delayed event emission via asyncio.sleep |

### `EventEmitter`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `source: str`, `event_bus: EventBus \| None` | `None` | Initialize with source ID and optional bus |
| `emit` | `event_type`, `data`, `correlation_id`, `metadata`, `priority` | `None` | Sync publish; no-op if disabled |
| `emit_sync` | (same as `emit`) | `None` | Alias for `emit` |
| `emit_async` | (same as `emit`) | `None` | Async publish via `bus.publish_async` |
| `emit_batch` | `events: list[dict]` | `None` | Sync publish multiple events |
| `emit_batch_async` | `events: list[dict]` | `None` | Async publish multiple events via `asyncio.gather` |
| `start_operation` | `operation_name: str`, `operation_data: dict \| None` | `str` | Emit start event, return correlation ID |
| `update_operation` | `correlation_id`, `operation_name`, `progress`, `status`, `data` | `None` | Emit progress event |
| `end_operation` | `correlation_id`, `operation_name`, `success`, `result`, `error` | `None` | Emit completion event, clear correlation context |
| `emit_error` | `error_type`, `error_message`, `context`, `correlation_id` | `None` | Emit SYSTEM_ERROR at priority 2 |
| `emit_metric` | `metric_name`, `value`, `metric_type`, `labels` | `None` | Emit METRIC_UPDATE event |
| `emit_alert` | `alert_name`, `level`, `message`, `threshold`, `current_value` | `None` | Emit ALERT_TRIGGERED with priority mapped from level |
| `enable` / `disable` | — | `None` | Toggle emission |
| `set_correlation_context` / `clear_correlation_context` | `correlation_id: str` | `None` | Manage default correlation ID |
| `set_default_metadata` | `metadata: dict` | `None` | Set metadata merged into all events |

### `EventOperationContext`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__enter__` | — | `self` | Start operation, record start time |
| `__exit__` | `exc_type`, `exc_val`, `exc_tb` | `None` | End operation with success/failure and duration |

## Dependencies

- **Internal**: `events.core.event_bus` (`EventBus`, `get_event_bus`), `events.core.event_schema` (`Event`, `EventType`)
- **External**: Standard library only (`asyncio`, `uuid`)

## Constraints

- `emit_batch` expects dicts with required key `event_type` and optional keys `data`, `correlation_id`, `metadata`, `priority`.
- The `enabled` flag is checked at the start of every emit method; disabled emitters silently discard events.
- `AsyncEventEmitter.emit_later` uses `asyncio.create_task` which requires a running event loop.
- Default metadata is copied (not referenced) when set via `set_default_metadata`.

## Error Handling

- `RuntimeError` and `AttributeError` from `EventBus.publish` are caught and logged in `emit()`.
- `emit_batch_async` uses `return_exceptions=True` in `asyncio.gather` to prevent one failure from blocking others.
- `EventOperationContext` does not suppress exceptions; it emits a failure event and re-raises.
