# Streaming Module

**Version**: v0.1.0 | **Status**: Active

Real-time data streaming with SSE, pub/sub, and stream processing.

## Key Exports

### Classes
- **`EventType`** — Standard event types.
- **`Event`** — A stream event.
- **`Subscription`** — A subscription to a stream.
- **`Stream`** — Abstract base class for streams.
- **`InMemoryStream`** — In-memory stream implementation.
- **`SSEStream`** — Server-Sent Events stream implementation.
- **`StreamProcessor`** — Process events from a stream with transformations.
- **`TopicStream`** — Stream with topic-based routing.

### Functions
- **`create_event()`** — Create a new event.

## Quick Start

```python
import asyncio
from codomyrmex.streaming import (
    InMemoryStream, SSEStream, Event, EventType, TopicStream, create_event
)

# Basic pub/sub streaming
stream = InMemoryStream()

async def handler(event):
    print(f"Received: {event.data}")

sub = await stream.subscribe(handler)
await stream.publish(Event(data={"message": "Hello!"}))

# Server-Sent Events (SSE)
sse = SSEStream()
sub = await sse.subscribe(lambda e: None, topic="updates")

# In your web framework
async for line in sse.sse_generator(sub.id):
    yield line  # "id: ...\nevent: message\ndata: {...}\n\n"

# Topic-based routing
topics = TopicStream()
await topics.subscribe("orders", order_handler)
await topics.publish("orders", Event(data={"order_id": "123"}))
```

## Stream Processor

```python
from codomyrmex.streaming import StreamProcessor

# Transform and filter events
processor = (
    StreamProcessor(source_stream)
    .filter(lambda e: e.data.get("priority") == "high")
    .map(lambda e: Event(data={**e.data, "processed": True}))
    .sink(target_stream)
)
await processor.start()
```

## Exports

| Class | Description |
|-------|-------------|
| `InMemoryStream` | In-memory pub/sub with event buffer |
| `SSEStream` | Server-Sent Events stream |
| `TopicStream` | Topic-based message routing |
| `StreamProcessor` | Transform/filter/sink pipeline |
| `Event` | Event with id, type, data, metadata |
| `EventType` | Enum: message, error, connect, disconnect, heartbeat |
| `Subscription` | Active subscription with cancel() |
| `create_event(data)` | Create event with defaults |
| `broadcast(streams, event)` | Send to multiple streams |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k streaming -v
```


## Documentation

- [Module Documentation](../../../docs/modules/streaming/README.md)
- [Agent Guide](../../../docs/modules/streaming/AGENTS.md)
- [Specification](../../../docs/modules/streaming/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
