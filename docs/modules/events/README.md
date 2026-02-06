# Events Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Event-driven architecture with pub/sub, event sourcing, and handlers.

## Key Features

- **Pub/Sub** — Publish/subscribe pattern
- **Event Store** — Event persistence
- **Handlers** — Async event handlers
- **Replay** — Event replay support

## Quick Start

```python
from codomyrmex.events import EventBus, Event, event_handler

class UserCreated(Event):
    user_id: str

@event_handler(UserCreated)
async def on_user_created(event):
    print(f"User {event.user_id} created")

bus = EventBus()
await bus.publish(UserCreated(user_id="123"))
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/events/](../../../src/codomyrmex/events/)
- **Parent**: [Modules](../README.md)
