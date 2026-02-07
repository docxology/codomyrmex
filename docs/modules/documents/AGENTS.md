# Documents Module — Agent Coordination

## Purpose

Documents Module for Codomyrmex.

## Key Capabilities

- Documents operations and management

## Agent Usage Patterns

```python
from codomyrmex.documents import *

# Agent uses documents capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/documents/](../../../src/codomyrmex/documents/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`DocumentsConfig`** — Configuration for document operations.
- **`DocumentsError`** — Base exception class for all Documents module errors.
- **`DocumentReadError`** — Raised when document reading fails.
- **`DocumentWriteError`** — Raised when document writing fails.
- **`DocumentParseError`** — Raised when document parsing fails.
- **`get_config()`** — Get the global documents configuration.
- **`set_config()`** — Set the global documents configuration.

### Submodules

- `core` — Core
- `formats` — Formats
- `metadata` — Metadata
- `models` — Models
- `search` — Search
- `transformation` — Transformation
- `utils` — Utilities

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k documents -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
