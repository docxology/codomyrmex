# Cache Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Multi-backend caching with memory, Redis, and disk storage options.

## Key Features

- **Memory** — In-memory LRU cache
- **Redis** — Redis-backed caching
- **Disk** — Persistent file cache
- **TTL** — Time-to-live expiration

## Quick Start

```python
from codomyrmex.cache import MemoryCache, cached

cache = MemoryCache(max_size=1000)
cache.set("key", "value", ttl=300)

@cached(ttl=60)
def expensive_function(x):
    return compute(x)
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/cache/](../../../src/codomyrmex/cache/)
- **Parent**: [Modules](../README.md)
