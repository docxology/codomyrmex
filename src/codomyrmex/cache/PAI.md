# Personal AI Infrastructure — Cache Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Cache module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.cache import Cache, CacheManager, CacheStats, replication, async_ops, warmers
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `replication` | Function/Constant | Replication |
| `async_ops` | Function/Constant | Async ops |
| `warmers` | Function/Constant | Warmers |
| `Cache` | Class | Cache |
| `CacheManager` | Class | Cachemanager |
| `CacheStats` | Class | Cachestats |
| `NamespacedCache` | Class | Namespacedcache |
| `TTLManager` | Class | Ttlmanager |
| `get_cache` | Function/Constant | Get cache |
| `CacheError` | Class | Cacheerror |
| `CacheExpiredError` | Class | Cacheexpirederror |
| `CacheFullError` | Class | Cachefullerror |
| `CacheConnectionError` | Class | Cacheconnectionerror |
| `CacheKeyError` | Class | Cachekeyerror |

*Plus 6 additional exports.*


## PAI Algorithm Phase Mapping

| Phase | Cache Contribution |
|-------|------------------------------|
| **OBSERVE** | Data gathering and state inspection |
| **VERIFY** | Validation and quality checks |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
