# Streaming API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## 1. Overview

The `streaming` module provides real-time data streaming patterns with support for Server-Sent Events (SSE), in-memory pub/sub, topic-based routing, and stream processing pipelines. All stream implementations share the abstract `Stream` base class with async publish/subscribe semantics.

## 2. Core Components

### 2.1 Enums

- **`EventType`**: Standard event types -- `MESSAGE`, `ERROR`, `CONNECT`, `DISCONNECT`, `HEARTBEAT`.

### 2.2 Data Classes

**`Event`**: Core event unit.
- `id: str` -- UUID, auto-generated.
- `type: EventType` -- Default `MESSAGE`.
- `data: Any` -- Event payload.
- `metadata: dict[str, Any]` -- Arbitrary metadata.
- `timestamp: datetime` -- Auto-set to `now()`.
- Methods: `to_dict()`, `to_sse()`, `Event.from_dict(data)`.

**`Subscription`**: Subscription handle.
- `id: str` -- UUID, auto-generated.
- `topic: str = "*"` -- Topic filter (`"*"` = all).
- `handler: Callable[[Event], None] | None` -- Event callback.
- `filter_fn: Callable[[Event], bool] | None` -- Additional filter.
- `active: bool` -- Cancellation flag.
- Methods: `cancel()`, `should_receive(event) -> bool`.

### 2.3 Stream Implementations

```python
from codomyrmex.streaming import InMemoryStream, SSEStream, TopicStream

# In-memory pub/sub
stream = InMemoryStream()
sub = await stream.subscribe(handler=my_callback, topic="orders")
await stream.publish(event)
await stream.unsubscribe(sub.id)
recent = stream.get_recent_events(count=20)

# SSE stream with async iteration
sse = SSEStream(buffer_size=100)
sub = await sse.subscribe(handler=on_event)
async for event in sse.events(sub.id):
    process(event)
async for sse_str in sse.sse_generator(sub.id):
    yield sse_str  # "id: ...\nevent: ...\ndata: ...\n\n"

# Topic-based routing
topics = TopicStream()
await topics.publish("user.signup", event)
sub = await topics.subscribe("user.signup", handler=on_signup)
topics.list_topics()  # -> ["user.signup"]
```

### 2.4 Stream (ABC)

All stream classes implement: `publish(event)`, `subscribe(handler, topic, filter_fn)`, `unsubscribe(subscription_id)`.

### 2.5 Stream Processor

```python
from codomyrmex.streaming import StreamProcessor

processor = StreamProcessor(source=input_stream)
processor \
    .filter(lambda e: e.type == EventType.MESSAGE) \
    .map(lambda e: transform(e)) \
    .sink(output_stream)

sub = await processor.start()
```

Supports chained `.map()`, `.filter()`, and `.sink()` operations. Returns subscription handle from `start()`.

### 2.6 Convenience Functions

```python
from codomyrmex.streaming import create_event, broadcast

event = create_event({"user": "alice"}, EventType.MESSAGE, topic="signup")
await broadcast([stream1, stream2, stream3], event)
```

## 3. Error Handling

Handler exceptions in `InMemoryStream` are silently caught to prevent one subscriber from affecting others. SSE timeouts (30s) automatically emit `HEARTBEAT` events.

## 4. Thread Safety

`InMemoryStream` uses `threading.Lock` for thread-safe publish/subscribe. `SSEStream` uses `asyncio.Queue` per subscription for async-safe delivery.

## 5. Integration Points

- **service_mesh**: Stream circuit breaker state change events.
- **logging_monitoring**: Forward events to structured logging.
- **notification**: Route stream events to notification channels.

## 6. Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
