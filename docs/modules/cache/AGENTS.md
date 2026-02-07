# Cache Module — Agent Coordination

## Purpose

Cache module for Codomyrmex.

## Key Capabilities

- `get_cache()`: Get a cache instance by name.

## Agent Usage Patterns

```python
from codomyrmex.cache import *

# Agent uses cache capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/cache/](../../../src/codomyrmex/cache/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`get_cache()`** — Get a cache instance by name.

### Submodules

- `async_ops` — Async Ops
- `backends` — Backends
- `distributed` — Distributed
- `invalidation` — Invalidation
- `policies` — Policies
- `replication` — Replication
- `serializers` — Serializers
- `warmers` — Warmers

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cache -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
