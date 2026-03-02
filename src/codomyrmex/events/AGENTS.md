# Agent Guidelines - Events

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Event-driven architecture for Codomyrmex providing synchronous and asynchronous event publishing, subscription-based routing with pattern matching, prioritized event handling, and comprehensive audit logging. The singleton `EventBus` is the central hub; `EventEmitter` wraps it for ergonomic use; `EventListener`/`AutoEventListener` manage subscriptions. All core components are thread-safe.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `get_event_bus`, `EventType`, `EventEmitter`, `EventListener` |
| `core/event_bus.py` | `EventBus` singleton with `publish`, `subscribe`, `get_event_bus` |
| `core/event_schema.py` | `Event`, `EventType`, `EventPriority` data models |
| `handlers/event_logger.py` | `get_event_logger` — `get_event_stats`, `get_recent_events` |
| `mcp_tools.py` | MCP tools: `emit_event`, `list_event_types`, `get_event_history` |

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `emit_event` | Emit an event to the bus. Accepts `event_type`, `payload`, `source`, `priority`. | SAFE |
| `list_event_types` | List all registered event type names in the EventType enum. | SAFE |
| `get_event_history` | Retrieve recent event history from `EventLogger`. Returns list of recent events. | SAFE |

## Agent Instructions

1. **Use the singleton bus** — Always call `get_event_bus()` for the central instance
2. **Typed events** — Prefer `EventType` enum; for custom topics use `domain.action` pattern (e.g., `git.commit`)
3. **Idempotent handlers** — Write event handlers that are safe to call multiple times
4. **Zero-Mock policy** — Use a real `EventBus` instance in tests; capture events via `EventListener`
5. **Thread-safe** — `EventBus`, `EventLogger`, `EventStore` are thread-safe; no locking needed in handlers

## Common Patterns

```python
from codomyrmex.events import get_event_bus, EventEmitter, EventType

# Emit an event via helper
emitter = EventEmitter(source="my_module")
emitter.emit(EventType.TASK_STARTED, data={"task_id": "abc123"})

# Subscribe to events
bus = get_event_bus()
bus.subscribe([EventType.TASK_COMPLETED], lambda e: print(e.data))

# Handler class pattern
from codomyrmex.events import AutoEventListener, event_handler

class MyAgent:
    @event_handler(EventType.ANALYSIS_COMPLETE)
    def on_complete(self, event):
        print(f"Analysis {event.data['id']} done")

listener = AutoEventListener(listener_id="agent_listener")
listener.register_handlers(MyAgent())
```

## Testing Patterns

```python
from codomyrmex.events import get_event_bus, EventType

bus = get_event_bus()
received = []
bus.subscribe([EventType.TASK_STARTED], lambda e: received.append(e))

# Trigger the event
bus.publish(EventType.TASK_STARTED, payload={"task": "test"})
assert len(received) == 1
assert received[0].data["task"] == "test"
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `emit_event`, `list_event_types`, `get_event_history` | TRUSTED |
| **Architect** | Design | `list_event_types`, `get_event_history` — review event taxonomy | OBSERVED |
| **QATester** | Validation | `get_event_history`, `list_event_types` — verify event flow during VERIFY | OBSERVED |
| **Researcher** | Read-only | `get_event_history`, `list_event_types` — inspect system activity | SAFE |

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
