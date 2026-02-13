# Personal AI Infrastructure — Events Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Event-Driven Architecture for Codomyrmex This is a **Service Layer** module.

## PAI Capabilities

```python
from codomyrmex.events import Event, EventType, EventPriority, get_event_bus, publish_event, subscribe_to_events
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Event` | Class | Event |
| `EventType` | Class | Eventtype |
| `EventPriority` | Class | Eventpriority |
| `EventSchema` | Class | Eventschema |
| `EventBus` | Class | Eventbus |
| `AsyncEventEmitter` | Class | Asynceventemitter |
| `EventLogger` | Class | Eventlogger |
| `EventMixin` | Class | Eventmixin |
| `get_event_bus` | Function/Constant | Get event bus |
| `publish_event` | Function/Constant | Publish event |
| `subscribe_to_events` | Function/Constant | Subscribe to events |
| `unsubscribe_from_events` | Function/Constant | Unsubscribe from events |
| `get_event_logger` | Function/Constant | Get event logger |
| `get_event_stats` | Function/Constant | Get event stats |
| `EventError` | Class | Eventerror |

*Plus 7 additional exports.*


## PAI Algorithm Phase Mapping

| Phase | Events Contribution |
|-------|------------------------------|
| **OBSERVE** | Data gathering and state inspection |
| **VERIFY** | Validation and quality checks |
| **LEARN** | Learning and knowledge capture |

## Architecture Role

**Service Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
