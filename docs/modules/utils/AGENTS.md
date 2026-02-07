# Utilities Module — Agent Coordination

## Purpose

Utilities Package.

## Key Capabilities

- `ensure_directory()`: Ensure a directory exists, creating it if necessary.
- `safe_json_loads()`: Safely parse JSON with a fallback default.
- `safe_json_dumps()`: Safely serialize to JSON with fallback.

## Agent Usage Patterns

```python
from codomyrmex.utils import *

# Agent uses utilities capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/utils/](../../../src/codomyrmex/utils/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k utils -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
