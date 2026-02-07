# Defense Module — Agent Coordination

## Purpose

Defense Module.

## Key Capabilities

- Defense operations and management

## Agent Usage Patterns

```python
from codomyrmex.defense import *

# Agent uses defense capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/defense/](../../../src/codomyrmex/defense/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`ActiveDefense`** — Active defense system against cognitive exploits.
- **`Defense`** — Main class for defense functionality.
- **`RabbitHole`** — A simulated environment to contain and waste the time of attackers.
- **`create_defense()`** — Create a new Defense instance.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k defense -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
