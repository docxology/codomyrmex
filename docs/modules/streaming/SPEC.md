# Streaming — Functional Specification

**Module**: `codomyrmex.streaming`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Real-time data streaming patterns with SSE and message broker support.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `EventType` | Class | Standard event types. |
| `Event` | Class | A stream event. |
| `Subscription` | Class | A subscription to a stream. |
| `Stream` | Class | Abstract base class for streams. |
| `InMemoryStream` | Class | In-memory stream implementation. |
| `SSEStream` | Class | Server-Sent Events stream implementation. |
| `StreamProcessor` | Class | Process events from a stream with transformations. |
| `TopicStream` | Class | Stream with topic-based routing. |
| `create_event()` | Function | Create a new event. |
| `to_dict()` | Function | Convert to dictionary. |
| `to_sse()` | Function | Convert to SSE format. |
| `from_dict()` | Function | Create from dictionary. |
| `cancel()` | Function | Cancel this subscription. |

### Source Files

- `async_stream.py`

## 3. Dependencies

See `src/codomyrmex/streaming/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.streaming import EventType, Event, Subscription, Stream, InMemoryStream
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k streaming -v
```
