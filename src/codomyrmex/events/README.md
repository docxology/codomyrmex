# events

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Event-Driven Architecture for Codomyrmex. Provides an asynchronous event bus for decoupling system components, implementing the Publish-Subscribe pattern with support for synchronous and asynchronous event handling, filtering, prioritization, and event logging.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `event_bus.py` – File
- `event_emitter.py` – File
- `event_listener.py` – File
- `event_logger.py` – File
- `event_schema.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.events import (
    EventBus, EventEmitter, EventListener, Event, EventType,
    publish_event, subscribe_to_events
)

# Using EventEmitter to publish events
emitter = EventEmitter(source="my_module")
emitter.emit(EventType.MODULE_LOAD, data={"module": "example"})

# Using EventListener to receive events
listener = EventListener(listener_id="my_listener")

def handle_event(event: Event):
    print(f"Received event: {event.event_type.value}")

listener.on(EventType.MODULE_LOAD, handle_event)

# Using global functions
publish_event(Event(
    event_type=EventType.SYSTEM_STARTUP,
    source="system",
    data={"version": "1.0.0"}
))

subscribe_to_events(
    event_types=[EventType.MODULE_LOAD],
    handler=handle_event
)
```

