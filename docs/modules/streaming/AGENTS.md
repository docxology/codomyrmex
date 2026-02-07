# Streaming Module — Agent Coordination

## Purpose

Real-time data streaming patterns with SSE and message broker support.

## Key Capabilities

- **EventType**: Standard event types.
- **Event**: A stream event.
- **Subscription**: A subscription to a stream.
- **Stream**: Abstract base class for streams.
- **InMemoryStream**: In-memory stream implementation.
- `create_event()`: Create a new event.
- `to_dict()`: Convert to dictionary.
- `to_sse()`: Convert to SSE format.

## Agent Usage Patterns

```python
from codomyrmex.streaming import EventType

# Agent initializes streaming
instance = EventType()
```

## Integration Points

- **Source**: [src/codomyrmex/streaming/](../../../src/codomyrmex/streaming/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k streaming -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
