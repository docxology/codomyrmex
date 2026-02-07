# Serialization Module — Agent Coordination

## Purpose

Serialization module for Codomyrmex.

## Key Capabilities

- `serialize()`: Serialize an object to bytes.
- `deserialize()`: Deserialize data to an object.

## Agent Usage Patterns

```python
from codomyrmex.serialization import *

# Agent uses serialization capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/serialization/](../../../src/codomyrmex/serialization/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`serialize()`** — Serialize an object to bytes.
- **`deserialize()`** — Deserialize data to an object.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k serialization -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
