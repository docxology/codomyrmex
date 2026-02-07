# IDE Integration Module — Agent Coordination

## Purpose

IDE Integration Module.

## Key Capabilities

- **IDEStatus**: Status of an IDE session.
- **IDECommand**: Represents an IDE command to be executed.
- **IDECommandResult**: Result of an IDE command execution.
- **FileInfo**: Information about a file in the IDE.
- **IDEClient**: Abstract base class for IDE integrations.
- `to_dict()`: to dict
- `to_dict()`: to dict
- `to_dict()`: to dict

## Agent Usage Patterns

```python
from codomyrmex.ide import IDEStatus

# Agent initializes ide integration
instance = IDEStatus()
```

## Integration Points

- **Source**: [src/codomyrmex/ide/](../../../src/codomyrmex/ide/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Related Modules

- [Exceptions](../exceptions/AGENTS.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k ide -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
