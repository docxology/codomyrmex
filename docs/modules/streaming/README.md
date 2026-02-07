# Streaming Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Real-time data streaming patterns with SSE and message broker support.

## Key Features

- **EventType** — Standard event types.
- **Event** — A stream event.
- **Subscription** — A subscription to a stream.
- **Stream** — Abstract base class for streams.
- **InMemoryStream** — In-memory stream implementation.
- **SSEStream** — Server-Sent Events stream implementation.
- `create_event()` — Create a new event.
- `to_dict()` — Convert to dictionary.
- `to_sse()` — Convert to SSE format.
- `from_dict()` — Create from dictionary.

## Quick Start

```python
from codomyrmex.streaming import EventType, Event, Subscription

# Initialize
instance = EventType()
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `EventType` | Standard event types. |
| `Event` | A stream event. |
| `Subscription` | A subscription to a stream. |
| `Stream` | Abstract base class for streams. |
| `InMemoryStream` | In-memory stream implementation. |
| `SSEStream` | Server-Sent Events stream implementation. |
| `StreamProcessor` | Process events from a stream with transformations. |
| `TopicStream` | Stream with topic-based routing. |

### Functions

| Function | Description |
|----------|-------------|
| `create_event()` | Create a new event. |
| `to_dict()` | Convert to dictionary. |
| `to_sse()` | Convert to SSE format. |
| `from_dict()` | Create from dictionary. |
| `cancel()` | Cancel this subscription. |
| `should_receive()` | Check if this subscription should receive an event. |
| `get_recent_events()` | Get recent events from buffer. |
| `map()` | Add a map transformation. |
| `filter()` | Add a filter transformation. |
| `sink()` | Add a sink to forward processed events. |
| `topic()` | Get or create a topic stream. |
| `list_topics()` | List all topics. |
| `filter_transform()` | filter transform |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/streaming/](../../../src/codomyrmex/streaming/)
- **Parent**: [Modules](../README.md)
