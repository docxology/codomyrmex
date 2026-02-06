# Personal AI Infrastructure — Events Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Events module provides PAI integration for event-driven architectures.

## PAI Capabilities

### Event Publishing

Publish events:

```python
from codomyrmex.events import EventBus, Event

class UserCreated(Event):
    user_id: str

bus = EventBus()
await bus.publish(UserCreated(user_id="123"))
```

### Event Handling

Handle events:

```python
from codomyrmex.events import event_handler

@event_handler(UserCreated)
async def on_user_created(event):
    print(f"User {event.user_id} created")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `EventBus` | Publish events |
| `event_handler` | Handle events |
| `EventStore` | Persist events |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
