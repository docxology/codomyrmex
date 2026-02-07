# Embodiment Module — Agent Coordination

## Purpose

Embodiment module for Codomyrmex.

## Key Capabilities

- Embodiment operations and management

## Agent Usage Patterns

```python
from codomyrmex.embodiment import *

# Agent uses embodiment capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/embodiment/](../../../src/codomyrmex/embodiment/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components


### Submodules

- `actuators` — Actuators
- `ros` — Ros
- `sensors` — Sensors
- `transformation` — Transformation

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k embodiment -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
