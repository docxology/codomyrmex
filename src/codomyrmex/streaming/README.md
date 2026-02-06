# Streaming Module

Real-time data streaming patterns with SSE and message routing.

## Features

- **Multiple Stream Types**: InMemory, SSE, Topic-based
- **Event Processing**: Map, filter, and route events
- **Async-first**: Built on asyncio for high performance
- **SSE Support**: Server-Sent Events for web clients

## Quick Start

```python
from codomyrmex.streaming import (
    InMemoryStream, SSEStream, TopicStream,
    Event, EventType, create_event,
)

# Basic streaming
stream = InMemoryStream()

async def handler(event):
    print(f"Received: {event.data}")

await stream.subscribe(handler)
await stream.publish(create_event({"message": "hello"}))

# Topic-based routing
topics = TopicStream()
await topics.subscribe("orders", handle_order)
await topics.subscribe("alerts", handle_alert)

await topics.publish("orders", create_event({"id": 123}))
```

## Navigation

- [Technical Spec](SPEC.md)
- [Agent Guidelines](AGENTS.md)
- [PAI Context](PAI.md)
