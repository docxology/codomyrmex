# Metrics Module — Agent Coordination

## Purpose

Metrics module for Codomyrmex.

## Key Capabilities

- **MetricsError**: Raised when metrics operations fail.
- `get_metrics()`: Get a metrics instance.

## Agent Usage Patterns

```python
from codomyrmex.metrics import MetricsError

# Agent initializes metrics
instance = MetricsError()
```

## Integration Points

- **Source**: [src/codomyrmex/metrics/](../../../src/codomyrmex/metrics/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)
