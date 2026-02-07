# Encryption Module — Agent Coordination

## Purpose

Encryption module for Codomyrmex.

## Key Capabilities

- `encrypt()`: Encrypt data.
- `decrypt()`: Decrypt data.
- `generate_key()`: Generate an encryption key.

## Agent Usage Patterns

```python
from codomyrmex.encryption import *

# Agent uses encryption capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/encryption/](../../../src/codomyrmex/encryption/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Related Modules

- [Exceptions](../exceptions/AGENTS.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k encryption -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
