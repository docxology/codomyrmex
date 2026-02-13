# Personal AI Infrastructure — Concurrency Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Concurrency and synchronization module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.concurrency import BaseLock, LocalLock, BaseSemaphore
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `BaseLock` | Class | Baselock |
| `LocalLock` | Class | Locallock |
| `BaseSemaphore` | Class | Basesemaphore |
| `LocalSemaphore` | Class | Localsemaphore |
| `RedisLock` | Class | Redislock |
| `LockManager` | Class | Lockmanager |
| `ReadWriteLock` | Class | Readwritelock |

## PAI Algorithm Phase Mapping

| Phase | Concurrency Contribution |
|-------|------------------------------|
| **EXECUTE** | General module operations |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
