# Agent Guidelines - Events

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

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

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `emit_event` | Emit an event to the event bus | Safe |
| `list_event_types` | List all registered event types in the event bus | Safe |
| `get_event_history` | Retrieve recent event history from the event bus | Safe |

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `emit_event`, `list_event_types`, `get_event_history`; full event bus control | TRUSTED |
| **Architect** | Read + Design | `list_event_types`, `get_event_history`; event schema review, pub/sub design | OBSERVED |
| **QATester** | Validation | `get_event_history`, `list_event_types`; event delivery verification | OBSERVED |

### Engineer Agent
**Use Cases**: Emitting workflow events during EXECUTE, configuring event subscriptions, auditing event history.

### Architect Agent
**Use Cases**: Designing event-driven workflows, reviewing event type taxonomy, pub/sub architecture analysis.

### QATester Agent
**Use Cases**: Verifying event delivery and ordering during VERIFY, confirming event history completeness.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
