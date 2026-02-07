# Authentication Module — Agent Coordination

## Purpose

Authentication module for Codomyrmex.

## Key Capabilities

- `authenticate()`: Authenticate with credentials.
- `authorize()`: Check if token has permission.
- `get_authenticator()`: Get an authenticator instance.

## Agent Usage Patterns

```python
from codomyrmex.auth import *

# Agent uses authentication capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/auth/](../../../src/codomyrmex/auth/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Related Modules

- [Exceptions](../exceptions/AGENTS.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k auth -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
