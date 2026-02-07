# Performance Module — Agent Coordination

## Purpose

Performance optimization utilities for Codomyrmex.

## Key Capabilities

- **performance_context**: No-op context manager if dependencies missing.
- `monitor_performance()`: No-op decorator if dependencies missing.
- `get_system_metrics()`: get system metrics
- `decorator()`: decorator

## Agent Usage Patterns

```python
from codomyrmex.performance import performance_context

# Agent initializes performance
instance = performance_context()
```

## Integration Points

- **Source**: [src/codomyrmex/performance/](../../../src/codomyrmex/performance/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)
