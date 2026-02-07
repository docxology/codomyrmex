# Privacy Module — Agent Coordination

## Purpose

Privacy Module.

## Key Capabilities

- Privacy operations and management

## Agent Usage Patterns

```python
from codomyrmex.privacy import *

# Agent uses privacy capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/privacy/](../../../src/codomyrmex/privacy/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`CrumbCleaner`** — Sanitizes data by removing tracking crumbs and metadata.
- **`Packet`** — Packet
- **`MixNode`** — A single node in the mixnet overlay.
- **`MixnetProxy`** — Manages anonymous routing through the mixnet.
- **`Privacy`** — Main class for privacy functionality.
- **`create_privacy()`** — Create a new Privacy instance.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k privacy -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
