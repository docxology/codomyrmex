# Agent Guidelines - Events

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Event-driven architecture with pub/sub, event sourcing, and handlers.

## Key Classes

- **EventBus** — Publish/subscribe hub
- **Event** — Base event class
- **EventHandler** — Event processing
- **EventStore** — Event persistence

## Agent Instructions

1. **Name events** — Use past tense (UserCreated)
2. **Include context** — Event ID, timestamp, actor
3. **Idempotent handlers** — Handle duplicates
4. **Order matters** — Preserve event order
5. **Log all events** — Audit trail

## Common Patterns

```python
from codomyrmex.events import EventBus, Event, event_handler

# Define events
class UserCreated(Event):
    user_id: str
    email: str

# Event handlers
@event_handler(UserCreated)
async def send_welcome_email(event: UserCreated):
    await send_email(event.email, "Welcome!")

# Publish events
bus = EventBus()
bus.register(send_welcome_email)

event = UserCreated(user_id="u1", email="user@example.com")
await bus.publish(event)

# Event store
store = EventStore()
store.append("user-stream", event)
events = store.load("user-stream")
```

## Testing Patterns

```python
# Verify event handling
handled = []
@event_handler(UserCreated)
def track(event):
    handled.append(event)

bus = EventBus()
bus.register(track)
await bus.publish(UserCreated(user_id="1", email="test@test.com"))
assert len(handled) == 1
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
