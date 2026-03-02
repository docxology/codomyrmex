# Events Streaming — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Async event streaming infrastructure providing multiple backend implementations (in-memory, SSE, topic-based, async with backpressure, WebSocket, batching) and a fluent stream processor for building event transformation pipelines.

## Architecture

Template method pattern via `Stream` ABC defining the async publish/subscribe interface. Each backend implements its own buffering and dispatch strategy. `StreamProcessor` implements a builder pattern for composing map/filter/sink chains. The streaming module defines its own `Event` and `EventType` distinct from `events.core` to support streaming-specific semantics (HEARTBEAT, CONNECT, DISCONNECT).

## Key Classes

### `Stream` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `publish` | `event: Event` | `None` | Publish event to the stream (async) |
| `subscribe` | `handler`, `topic: str = "*"`, `filter_fn` | `Subscription` | Subscribe to events (async) |
| `unsubscribe` | `subscription_id: str` | `bool` | Remove subscription (async) |

### `InMemoryStream`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `publish` | `event: Event` | `None` | Thread-safe publish with bounded buffer (1000) |
| `subscribe` | `handler`, `topic`, `filter_fn` | `Subscription` | Register handler |
| `get_recent_events` | `count: int = 10` | `list[Event]` | Get last N events from buffer |

### `SSEStream`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `publish` | `event: Event` | `None` | Publish to subscriber queues |
| `events` | `subscription_id: str` | `AsyncIterator[Event]` | Async iterator with 30s heartbeat timeout |
| `sse_generator` | `subscription_id: str` | `AsyncIterator[str]` | SSE-formatted string iterator |

### `AsyncStream`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `buffer_size: int = 1000`, `enable_backpressure: bool = True` | `None` | Configure bounded queue |
| `start` / `stop` | — | `None` | Start/stop dispatcher loop |
| `publish` | `event: Event` | `bool` | Publish with 5s timeout; returns False on timeout |
| `subscribe` | `buffer_size: int = 100` | `str` | Create subscriber queue, return ID |
| `consume` | `sub_id: str` | `AsyncIterator[Event]` | Async iterator with heartbeat on timeout |

### `WebSocketStream`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `connect` | `websocket: Any`, `client_id: str` | `str` | Register WebSocket, return subscription ID |
| `disconnect` | `client_id: str` | `None` | Unregister client |
| `broadcast` | `event: Event` | `None` | Send to all clients |
| `send_to` | `client_id: str`, `event: Event` | `bool` | Send to specific client |

### `BatchingStream`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `batch_size: int = 100`, `flush_interval: float = 1.0` | `None` | Configure batch parameters |
| `start` / `stop` | — | `None` | Start/stop periodic flush loop |
| `add` | `event: Event` | `None` | Add event to current batch |
| `on_batch` | `handler: Callable[[list[Event]], None]` | `None` | Register batch handler |

### `StreamProcessor`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `map` | `fn: Callable[[Event], Event]` | `self` | Add map transformation (chainable) |
| `filter` | `fn: Callable[[Event], bool]` | `self` | Add filter (chainable) |
| `sink` | `target: Stream` | `self` | Add output stream (chainable) |
| `start` | — | `Subscription` | Start processing pipeline |

## Dependencies

- **Internal**: None (self-contained models)
- **External**: Standard library only (`asyncio`, `threading`, `json`, `uuid`, `datetime`, `abc`, `collections.abc`)

## Constraints

- `InMemoryStream` buffer evicts oldest event when exceeding 1000 entries (FIFO).
- `SSEStream` and `AsyncStream` emit `HEARTBEAT` events after 30 seconds of inactivity per subscriber.
- `AsyncStream.publish()` returns `False` (not raises) when the buffer is full after 5 seconds.
- `BatchingStream._flush()` uses `asyncio.Lock` to prevent concurrent flush races.
- `TopicStream` creates new `InMemoryStream` instances lazily per topic name.
- `StreamProcessor.start()` creates an asyncio task per event for pipeline processing.
- The streaming `Event` and `EventType` are distinct types from `events.core` -- they are not interchangeable.

## Error Handling

- `InMemoryStream.publish()` catches handler exceptions (ValueError, RuntimeError, AttributeError, OSError, TypeError) and logs warnings.
- `AsyncStream._broadcast()` catches `asyncio.QueueFull` and silently drops events for slow subscribers.
- `AsyncStream.stop()` catches `asyncio.CancelledError` during dispatcher task cleanup.
- `BatchingStream._flush()` catches handler exceptions and logs them without propagation.
- `WebSocketStream.send_to()` catches send errors and returns `False` rather than raising.
