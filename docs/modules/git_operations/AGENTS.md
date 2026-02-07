# Git Operations Module — Agent Coordination

## Purpose

Git Operations Module for Codomyrmex.

## Key Capabilities

- Git Operations operations and management

## Agent Usage Patterns

```python
from codomyrmex.git_operations import *

# Agent uses git operations capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/git_operations/](../../../src/codomyrmex/git_operations/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Related Modules

- [Exceptions](../exceptions/AGENTS.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k git_operations -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
