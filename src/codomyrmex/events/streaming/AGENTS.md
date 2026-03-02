# Codomyrmex Agents — src/codomyrmex/events/streaming

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides async event streaming infrastructure with multiple backend implementations: in-memory streams with thread-safe buffering, Server-Sent Events (SSE) streams, topic-based routing, async streams with backpressure, WebSocket integration, batching streams, and a fluent stream processor for map/filter/sink pipelines.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `EventType` | Enum: MESSAGE, ERROR, CONNECT, DISCONNECT, HEARTBEAT (streaming-specific, distinct from `events.core.EventType`) |
| `models.py` | `Event` | Streaming event dataclass with id, type, data, metadata, timestamp; supports `to_dict()`, `to_sse()`, `from_dict()` |
| `models.py` | `Subscription` | Dataclass with topic, handler, filter_fn, active flag; `should_receive()` evaluates topic and filter match; `cancel()` deactivates |
| `models.py` | `create_event()` | Factory function for creating stream events |
| `stream.py` | `Stream` | ABC defining `publish()`, `subscribe()`, `unsubscribe()` async interface |
| `stream.py` | `InMemoryStream` | Thread-safe in-memory stream with bounded event buffer (default 1000) |
| `stream.py` | `SSEStream` | SSE stream with per-subscriber `asyncio.Queue`; yields `Event` or heartbeats on timeout; `sse_generator()` produces SSE-formatted strings |
| `stream.py` | `TopicStream` | Topic-based router creating isolated `InMemoryStream` instances per topic |
| `stream.py` | `broadcast()` | Async function publishing an event to multiple streams via `asyncio.gather` |
| `async_stream.py` | `AsyncStream` | Async-first stream with backpressure via bounded `asyncio.Queue`, a dispatcher loop, and `consume()` async iterator |
| `async_stream.py` | `WebSocketStream` | WebSocket adapter wrapping `AsyncStream` with `connect()`, `disconnect()`, `broadcast()`, and `send_to()` for individual clients |
| `async_stream.py` | `BatchingStream` | Batches events by count or time interval; flushes to registered batch handlers |
| `processors.py` | `StreamProcessor` | Fluent pipeline: `map()`, `filter()`, `sink()` transformations on a source `Stream` |

## Operating Contracts

- `InMemoryStream` is thread-safe via `threading.Lock`; handler exceptions are logged but not propagated.
- `SSEStream.events()` yields `Event(type=EventType.HEARTBEAT)` after 30 seconds of inactivity.
- `AsyncStream.publish()` times out after 5 seconds if the buffer is full and returns `False`.
- `AsyncStream._broadcast()` drops events for subscribers whose queues are full (backpressure).
- `BatchingStream` flushes when either `batch_size` is reached or `flush_interval` elapses.
- `StreamProcessor.filter()` wraps the predicate so filtered events return `None` and are dropped from the pipeline.
- `Subscription.should_receive()` checks `active` flag, topic match, and optional `filter_fn`.

## Integration Points

- **Depends on**: Standard library only (`asyncio`, `threading`, `json`, `uuid`, `datetime`, `collections.abc`)
- **Used by**: Real-time dashboards, SSE endpoints, WebSocket handlers, and any module requiring event streaming

## Navigation

- **Parent**: [events](../README.md)
- **Root**: [Codomyrmex](../../../../../README.md)
