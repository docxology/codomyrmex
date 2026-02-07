# Concurrency Module — Agent Coordination

## Purpose

Concurrency and synchronization module for Codomyrmex.

## Key Capabilities

- Concurrency operations and management

## Agent Usage Patterns

```python
from codomyrmex.concurrency import *

# Agent uses concurrency capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/concurrency/](../../../src/codomyrmex/concurrency/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`BaseLock`** — Abstract base class for all lock implementations.
- **`LocalLock`** — File-based lock for local multi-process synchronization.
- **`LockStats`** — Statistics for lock manager telemetry.
- **`LockManager`** — Orchestrates multiple locks and provides multi-resource acquisition.
- **`ReadWriteLock`** — In-process Read-Write lock (shared/exclusive).

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k concurrency -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
