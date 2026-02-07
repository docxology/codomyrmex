# Dark Module — Agent Coordination

## Purpose

Dark modes module - network, hardware, software, PDF dark mode utilities.

## Key Capabilities

- Dark operations and management

## Agent Usage Patterns

```python
from codomyrmex.dark import *

# Agent uses dark capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/dark/](../../../src/codomyrmex/dark/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components


### Submodules

- `hardware` — Hardware
- `network` — Network
- `pdf` — Pdf
- `software` — Software

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k dark -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
