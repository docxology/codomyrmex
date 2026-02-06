# Technical Specification - Streaming

**Module**: `codomyrmex.streaming`  
**Version**: v0.1.0  
**Last Updated**: February 2026

## 1. Purpose

Real-time data streaming with SSE, topic routing, and event processing.

## 2. Public API

```python
from codomyrmex.streaming import (
    Stream,           # ABC
    InMemoryStream,   # In-memory pub/sub
    SSEStream,        # Server-Sent Events
    TopicStream,      # Topic-based routing
    StreamProcessor,  # Event transformation
    Event,            # Event data class
    EventType,        # Event type enum
    Subscription,     # Subscription handle
    create_event,     # Factory function
    broadcast,        # Multi-stream publish
)
```

## 3. Event Types

| Type | Description |
|------|-------------|
| `MESSAGE` | Standard data event |
| `ERROR` | Error notification |
| `CONNECT` | Client connected |
| `DISCONNECT` | Client disconnected |
| `HEARTBEAT` | Keep-alive ping |

## 4. Testing

```bash
pytest tests/unit/test_streaming.py -v
```
