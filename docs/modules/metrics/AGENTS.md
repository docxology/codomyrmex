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

## Related Modules

- [Exceptions](../exceptions/AGENTS.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k metrics -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
