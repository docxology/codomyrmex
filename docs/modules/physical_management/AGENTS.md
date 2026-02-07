# Physical Management Module — Agent Coordination

## Purpose

Physical Object Management Module for Codomyrmex.

## Key Capabilities

- Physical Management operations and management

## Agent Usage Patterns

```python
from codomyrmex.physical_management import *

# Agent uses physical management capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/physical_management/](../../../src/codomyrmex/physical_management/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`AnalyticsMetric`** — Types of analytics metrics.
- **`StreamingMode`** — Streaming modes for data processing.
- **`DataPoint`** — A single data point in a stream.
- **`AnalyticsWindow`** — Time window for analytics calculations.
- **`DataStream`** — Real-time data stream with analytics capabilities.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k physical_management -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
