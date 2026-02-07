# Telemetry Module — Agent Coordination

## Purpose

Telemetry module for Codomyrmex.

## Key Capabilities

- Telemetry operations and management

## Agent Usage Patterns

```python
from codomyrmex.telemetry import *

# Agent uses telemetry capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/telemetry/](../../../src/codomyrmex/telemetry/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components


### Submodules

- `alerting` — Alerting
- `context` — Context
- `exporters` — Exporters
- `metrics` — Metrics
- `sampling` — Sampling
- `spans` — Spans
- `tracing` — Tracing

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k telemetry -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
