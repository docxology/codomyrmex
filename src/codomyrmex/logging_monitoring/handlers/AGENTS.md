# Codomyrmex Agents -- src/codomyrmex/logging_monitoring/handlers

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides specialized log handlers: an EventBus-to-log bridge for converting
typed events into structured JSON log entries, a WebSocket handler for
real-time log streaming with backpressure management, rotating file handlers
with disk monitoring, and a performance logger for timing operations.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `event_bridge.py` | `EventLoggingBridge` | Subscribes to `EventBus` typed events and logs each as structured JSON with correlation ID threading |
| `ws_handler.py` | `WebSocketLogHandler` | `logging.Handler` subclass pushing records to async queues for WebSocket broadcast with drop-oldest backpressure |
| `rotation.py` | `LogRotationManager` | Manages `RotatingFileHandler` attachment, disk usage monitoring, and old log cleanup |
| `performance.py` | `PerformanceLogger` | Timing operations via start/end timer, context manager, and metric logging |

## Operating Contracts

- `EventLoggingBridge` must call `start()` to subscribe and `stop()` to unsubscribe from the EventBus.
- `WebSocketLogHandler` drops oldest entries when queues are full (backpressure).
- `LogRotationManager` creates the log directory on initialization if it does not exist.
- `PerformanceLogger.time_operation()` context manager logs duration even on exception.
- `LogRotationManager.cleanup_old_logs()` removes files older than `max_age_days` (default 30).
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `events.core.event_bus.EventBus`, `events.core.event_schema.Event/EventType`, stdlib `logging`, `asyncio`
- **Used by**: Observability pipeline, WebSocket log viewers, performance monitoring

## Navigation

- **Parent**: [logging_monitoring](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
