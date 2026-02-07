# Networking Module — Agent Coordination

## Purpose

Networking module for Codomyrmex.

## Key Capabilities

- `get_http_client()`: Get an HTTP client instance.

## Agent Usage Patterns

```python
from codomyrmex.networking import *

# Agent uses networking capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/networking/](../../../src/codomyrmex/networking/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Related Modules

- [Exceptions](../exceptions/AGENTS.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k networking -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
