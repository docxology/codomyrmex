# Agent Guidelines - Events

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Event-driven architecture for Codomyrmex providing synchronous and asynchronous event publishing, subscription-based routing with pattern matching, prioritized event handling, and comprehensive audit logging. The singleton `EventBus` is the central hub; `AsyncEventEmitter` wraps it for ergonomic use; `EventListener`/`AutoEventListener` manage subscriptions with lifecycle control. `EventLogger` provides structured logging with statistics and performance reporting. `EventStore` is a separate append-only stream with sequence numbers and topic indexing. All core components are thread-safe.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `EventBus`, `Event`, `EventType`, `EventPriority`, `AsyncEventEmitter`, `EventListener`, `EventLogger`, `EventMixin`, `get_event_bus`, `publish_event`, `subscribe_to_events` |
| `core/event_bus.py` | `EventBus` singleton: `publish()`, `subscribe()`, `unsubscribe()`, `emit_typed()`, `subscribe_typed()`, `get_stats()`, `shutdown()`; module-level `get_event_bus()`, `publish_event()`, `subscribe_to_events()` |
| `core/event_schema.py` | `Event`, `EventType` enum, `EventPriority` enum, `EventSchema` data models |
| `core/exceptions.py` | Event-specific exceptions: `EventPublishError`, `EventSubscriptionError`, `EventHandlerError`, `EventTimeoutError`, `EventValidationError`, `EventQueueError`, `EventDeliveryError` |
| `core/mixins.py` | `EventMixin` for adding event capabilities to any class |
| `emitters/emitter.py` | `AsyncEventEmitter` for ergonomic async event emission |
| `handlers/event_listener.py` | `EventListener`, `AutoEventListener`, `event_handler` decorator, `create_listener()`, `create_auto_listener()` |
| `handlers/event_logger.py` | `EventLogger`, `EventLogEntry`: event history, statistics, performance reporting, log export; `get_event_logger()`, `get_event_stats()` |
| `event_store.py` | `EventStore`: append-only stream with `StreamEvent`, sequence numbers, topic indexing, range queries, compaction |
| `mcp_tools.py` | MCP tools: `emit_event`, `list_event_types`, `get_event_history` |

## Key Classes

- **EventBus** -- Central singleton hub for event routing. Thread-safe with `RLock`. Supports pattern matching via `fnmatch`, prioritized handler dispatch, async handler offloading via `ThreadPoolExecutor`, dead letter queue, and metrics (`events_published`, `events_processed`, `events_failed`).
- **Event** -- Core event dataclass with `event_type`, `data`, `source`, `priority`, `correlation_id`, `event_id`, `metadata`.
- **EventType** -- Enum of standard event types (`TASK_STARTED`, `TASK_COMPLETED`, `ANALYSIS_START`, `BUILD_START`, `SYSTEM_ERROR`, `CUSTOM`, etc.).
- **EventPriority** -- Enum of priority levels (`debug`, `info`, `normal`, `warning`, `error`, `critical`).
- **EventListener** -- Subscription lifecycle manager with `on()`, `once()`, `off()` methods and convenience helpers (`listen_to_analysis_events()`, `listen_to_build_events()`).
- **AutoEventListener** -- Extends `EventListener` to auto-register handlers decorated with `@event_handler` from any object.
- **AsyncEventEmitter** -- Ergonomic wrapper for emitting events with a fixed `source` identifier.
- **EventLogger** -- Subscribes to all events (`*` pattern), maintains history in a bounded `deque`, tracks per-type counts and processing times. Provides `get_event_statistics()`, `get_recent_events()`, `get_performance_report()`, `export_logs()`.
- **EventLogEntry** -- Wraps an `Event` with additional metadata: `timestamp`, `handler_count`, `processing_time`.
- **EventStore** -- Append-only stream with `StreamEvent` entries. Supports `read()` by sequence range, `read_by_topic()`, `read_by_time()`, `compact()` for old event removal. Thread-safe with `RLock`.
- **StreamEvent** -- Dataclass for the EventStore: `sequence`, `topic`, `event_type`, `data`, `timestamp`, `source`.
- **Subscription** -- Internal dataclass binding subscriber ID, event patterns, handler, filter function, and priority.

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `emit_event` | Emit an event to the bus. Accepts `event_type`, `payload`, `source`, `priority`. | SAFE |
| `list_event_types` | List all registered event type names in the EventType enum. | SAFE |
| `get_event_history` | Retrieve recent event history from `EventLogger`. Returns list of recent events. | SAFE |

## Agent Instructions

1. **Use the singleton bus** -- Always call `get_event_bus()` for the central instance
2. **Typed events** -- Prefer `EventType` enum; for custom topics use `domain.action` pattern (e.g., `git.commit`)
3. **Idempotent handlers** -- Write event handlers that are safe to call multiple times
4. **Zero-Mock policy** -- Use a real `EventBus` instance in tests; capture events via `EventListener`
5. **Thread-safe** -- `EventBus`, `EventLogger`, `EventStore` are thread-safe; no external locking needed in handlers

## Operating Contracts

- Events are immutable after publication: handlers must not mutate `Event.data` or any `Event` fields.
- `EventBus.subscribe()` requires a non-empty `event_patterns` list; empty patterns raise `EventSubscriptionError`.
- `EventBus.publish()` requires `event.event_type` to be set; missing type raises `EventPublishError`.
- `EventLogger` subscribes to all events via the `*` wildcard pattern; it must be instantiated after the `EventBus` to capture events.
- `EventStore` is append-only: `append()` assigns monotonically increasing sequence numbers. `compact()` is the only removal mechanism.
- `EventStore.compact(before_seq)` rebuilds topic indices after removal; callers must not hold references to removed events.
- Handlers that fail do not prevent other handlers from executing; failures increment `events_failed` and errors are logged.
- Failed events that cause top-level processing errors are added to the `dead_letter_queue`.
- `EventBus.shutdown()` terminates the thread pool and clears all subscriptions; the bus is not reusable after shutdown.
- **DO NOT** instantiate multiple `EventBus` singletons -- use `get_event_bus()` exclusively.
- **DO NOT** rely on handler execution order unless handlers have different `priority` values (higher = first).

## Common Patterns

```python
from codomyrmex.events import get_event_bus, AsyncEventEmitter, EventType

# Emit an event via helper
emitter = AsyncEventEmitter(source="my_module")
emitter.emit(EventType.TASK_STARTED, data={"task_id": "abc123"})

# Subscribe to events
bus = get_event_bus()
bus.subscribe([EventType.TASK_COMPLETED], lambda e: print(e.data))

# Handler class pattern
from codomyrmex.events.handlers.event_listener import AutoEventListener, event_handler

class MyAgent:
    @event_handler(EventType.ANALYSIS_COMPLETE)
    def on_complete(self, event):
        print(f"Analysis {event.data['id']} done")

listener = AutoEventListener(listener_id="agent_listener")
listener.register_handlers(MyAgent())
```

### Event Store Usage

```python
from codomyrmex.events.event_store import EventStore, StreamEvent

store = EventStore()
seq = store.append(StreamEvent(topic="agent", event_type="started", data={"agent_id": "a1"}))
events = store.read_by_topic("agent")
```

## Testing Patterns

```python
from codomyrmex.events import get_event_bus, EventType
from codomyrmex.events.core.event_schema import Event

bus = get_event_bus()
received = []
bus.subscribe([EventType.TASK_STARTED], lambda e: received.append(e))

# Trigger the event
bus.publish(Event(event_type=EventType.TASK_STARTED, data={"task": "test"}))
assert len(received) == 1
assert received[0].data["task"] == "test"
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `emit_event`, `list_event_types`, `get_event_history` | TRUSTED |
| **Architect** | Design | `list_event_types`, `get_event_history` -- review event taxonomy | OBSERVED |
| **QATester** | Validation | `get_event_history`, `list_event_types` -- verify event flow during VERIFY | OBSERVED |
| **Researcher** | Read-only | `get_event_history`, `list_event_types` -- inspect system activity | SAFE |

### Engineer Agent
**Use Cases**: Emitting `TASK_STARTED`/`TASK_COMPLETED` during EXECUTE, subscribing to `SYSTEM_ERROR` for reactive behavior, setting up event-driven pipeline routing.

### Architect Agent
**Use Cases**: Reviewing event taxonomy and naming conventions, designing cross-module event flows.

### QATester Agent
**Use Cases**: Verifying expected events are emitted during workflow execution during VERIFY phase.

### Researcher Agent
**Use Cases**: Inspecting event history to understand system activity patterns, auditing event flow.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/events.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/events.cursorrules)
