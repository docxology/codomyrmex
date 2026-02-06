# Agent Guidelines - Streaming

## Module Overview

Real-time event streaming for agent communication and live data feeds.

## Key Classes

- **Stream** — Base interface for all stream types
- **InMemoryStream** — Fast in-process communication
- **SSEStream** — Server-Sent Events for web clients
- **TopicStream** — Route events by topic
- **StreamProcessor** — Transform and route events

## Agent Instructions

1. **Use topics** — Organize event domains with `TopicStream`
2. **Handle errors** — Event handlers should catch exceptions
3. **Send heartbeats** — Keep long-lived SSE connections alive
4. **Buffer events** — Use replay buffers for late subscribers
5. **Clean up subscriptions** — Unsubscribe when done

## Common Patterns

```python
from codomyrmex.streaming import SSEStream, TopicStream, create_event

# Set up topic-based streaming
stream = TopicStream()

# Subscribe to topics
stream.subscribe("user_events", lambda e: handle_user_event(e))
stream.subscribe("system_alerts", lambda e: handle_alert(e))

# Publish events
stream.publish("user_events", create_event("login", {"user_id": 123}))

# SSE for web clients
sse = SSEStream()
async def sse_endpoint():
    async for event in sse:
        yield event.to_sse()
```

## Testing Patterns

```python
# Verify event routing
stream = TopicStream()
received = []
stream.subscribe("test", lambda e: received.append(e))
stream.publish("test", {"msg": "hello"})
assert len(received) == 1

# Verify SSE format
sse = SSEStream()
event = sse.format_event("update", {"data": 1})
assert "data:" in event
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
