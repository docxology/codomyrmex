# Spatial Module — Agent Coordination

## Purpose

Spatial modeling module for Codomyrmex.

## Key Capabilities

- Spatial operations and management

## Agent Usage Patterns

```python
from codomyrmex.spatial import *

# Agent uses spatial capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/spatial/](../../../src/codomyrmex/spatial/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components


### Submodules

- `coordinates` — Coordinates
- `four_d` — Four D
- `physics` — Physics
- `rendering` — Rendering
- `three_d` — Three D
- `world_models` — World Models

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k spatial -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
