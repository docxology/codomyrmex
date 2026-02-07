# Events Module — Agent Coordination

## Purpose

Event-Driven Architecture for Codomyrmex

## Key Capabilities

- Events operations and management

## Agent Usage Patterns

```python
from codomyrmex.events import *

# Agent uses events capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/events/](../../../src/codomyrmex/events/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Related Modules

- [Exceptions](../exceptions/AGENTS.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k events -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
