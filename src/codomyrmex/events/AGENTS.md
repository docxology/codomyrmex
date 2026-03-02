# Agent Guidelines - Events

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

The `events` module provides a robust event-driven architecture for Codomyrmex. It supports synchronous and asynchronous event publishing, subscription-based routing with pattern matching, prioritized event handling, and comprehensive audit logging.

## Core Directives

1. **Use the Singleton Bus**: Always use `get_event_bus()` to obtain the central event bus instance unless a dedicated bus is required for isolation.
2. **Typed Events**: Prefer `EventType` enum members for event types. If using custom strings, ensure they follow the `domain.action` pattern (e.g., `git.commit`).
3. **Zero-Mock Testing**: When testing components that use events, do not mock the `EventBus`. Instead, use a real `EventBus` instance and verify side effects or use a dedicated `EventListener` to capture emitted events.
4. **Idempotency**: Event handlers should be idempotent where possible, as the system may occasionally deliver the same event more than once in complex retry scenarios.
5. **Thread Safety**: All core components (`EventBus`, `EventLogger`, `EventStore`) are thread-safe.

## Key Classes and Usage

### EventBus
The central hub for all events.
- `subscribe(patterns, handler)`: Subscribe to event types (supports shell-style wildcards like `system.*`).
- `publish(event)`: Dispatch an event to all matching subscribers.

### EventEmitter
A helper for components to emit events with pre-configured source and metadata.
```python
emitter = EventEmitter(source="my_module")
emitter.emit(EventType.TASK_STARTED, data={"id": "123"})
```

### EventListener
A base class for components that need to manage multiple subscriptions.
- `on(type, handler)`: Register a handler.
- `once(type, handler)`: Register a handler that unsubscribes itself after one execution.

### AutoEventListener & @event_handler
The preferred way to define handlers within a class.
```python
class MyAgent:
    @event_handler(EventType.ANALYSIS_COMPLETE)
    def on_complete(self, event):
        print(f"Analysis {event.data['id']} finished")

agent = MyAgent()
listener = AutoEventListener(listener_id="agent_listener")
listener.register_handlers(agent)
```

## Logging and Statistics
Use `get_event_logger()` to access the global event history and performance metrics.
- `get_event_stats()`: Get counts of events by type.
- `get_recent_events(limit)`: Retrieve the last N events.

## MCP Tools Available

- `emit_event`: Emit an event (Safe)
- `list_event_types`: List active event types (Safe)
- `get_event_history`: Retrieve recent history (Safe)

## PAI Integration

| Phase | Usage |
|-------|-------|
| **EXECUTE** | Emit `TASK_STARTED`, `TASK_COMPLETED`, `TASK_FAILED` to track progress. |
| **OBSERVE** | Subscribe to `SYSTEM_ERROR` or `METRIC_UPDATE` to monitor system health. |
| **LEARN** | Analyze `EventLogger` history to optimize workflow patterns. |
