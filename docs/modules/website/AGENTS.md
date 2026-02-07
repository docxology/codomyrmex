# Website Module — Agent Coordination

## Purpose

Website generation module for Codomyrmex.

## Key Capabilities

- Website operations and management

## Agent Usage Patterns

```python
from codomyrmex.website import *

# Agent uses website capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/website/](../../../src/codomyrmex/website/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`DataProvider`** — Aggregates data from various system modules to populate the website.
- **`WebsiteGenerator`** — Generates the static website.
- **`WebsiteServer`** — Enhanced HTTP server that supports API endpoints for dynamic functionality.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k website -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
