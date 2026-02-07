# Compression Module — Agent Coordination

## Purpose

Compression module for Codomyrmex.

## Key Capabilities

- `compress()`: Compress data.
- `decompress()`: Decompress data.
- `get_compressor()`: Get a compressor instance.

## Agent Usage Patterns

```python
from codomyrmex.compression import *

# Agent uses compression capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/compression/](../../../src/codomyrmex/compression/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Related Modules

- [Exceptions](../exceptions/AGENTS.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k compression -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
