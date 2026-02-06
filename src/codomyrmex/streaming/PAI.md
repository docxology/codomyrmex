# Personal AI Infrastructure — Streaming Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Streaming module provides PAI integration for streaming data processing.

## PAI Capabilities

### Stream Processing

Process streaming data:

```python
from codomyrmex.streaming import Stream

async for chunk in Stream.from_llm(response):
    print(chunk, end="", flush=True)
```

### Event Streaming

Stream events:

```python
from codomyrmex.streaming import EventStream

stream = EventStream()
async for event in stream.subscribe("logs"):
    print(f"Event: {event}")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Stream` | Process streams |
| `EventStream` | Event streaming |
| `StreamBuffer` | Buffer management |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
