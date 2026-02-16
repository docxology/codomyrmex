# Cache Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Unified caching module providing multiple backend strategies for code analysis results, LLM responses, build artifacts, and other frequently accessed data. Features an abstract `Cache` interface with in-memory, file-based, and Redis backends; a `CacheManager` for named cache instance lifecycle; namespace isolation; TTL management; eviction policies; invalidation strategies; serializers; distributed caching; cache warmers; replication; and async operations.


## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Core Classes

- **`Cache`** -- Abstract base class defining the cache contract with `get()`, `set()`, `delete()`, `clear()`, and `exists()` methods
- **`CacheManager`** -- Factory and registry for named cache instances; creates caches with the specified backend (`in_memory`, `file_based`, `redis`)
- **`CacheStats`** -- Statistics tracker recording hits, misses, evictions, and size for cache performance monitoring
- **`NamespacedCache`** -- Cache wrapper that prefixes all keys with a namespace string for isolation between consumers
- **`TTLManager`** -- Manages time-to-live expiration for cache entries

### Functions

- **`get_cache(name, backend)`** -- Convenience function to obtain a named cache instance via the CacheManager

### Exceptions

- **`CacheError`** -- Base exception for all cache-related errors
- **`CacheExpiredError`** -- Raised when accessing an entry that has exceeded its TTL
- **`CacheFullError`** -- Raised when the cache has reached its capacity limit
- **`CacheConnectionError`** -- Raised when connection to a remote cache backend fails
- **`CacheKeyError`** -- Raised for invalid or missing cache keys
- **`CacheSerializationError`** -- Raised when serialization or deserialization of cache values fails
- **`CacheInvalidationError`** -- Raised when a cache invalidation operation fails

### Submodules

- **`policies`** -- Cache eviction policies (LRU, LFU, FIFO, etc.)
- **`invalidation`** -- Cache invalidation strategies (tag-based, pattern-based, event-driven)
- **`distributed`** -- Distributed cache coordination and consistency
- **`serializers`** -- Pluggable serializers for cache value encoding (JSON, pickle, msgpack)
- **`warmers`** -- Cache warming utilities for pre-populating caches at startup
- **`async_ops`** -- Async-compatible cache operations for use with asyncio
- **`replication`** -- Cache replication across multiple nodes

## Directory Contents

- `cache.py` -- `Cache` abstract base class with the cache interface contract
- `cache_manager.py` -- `CacheManager` factory for creating and managing named cache instances
- `stats.py` -- `CacheStats` for tracking cache hit rates and performance metrics
- `namespaced.py` -- `NamespacedCache` wrapper for key-prefix isolation
- `ttl_manager.py` -- `TTLManager` for time-based entry expiration
- `exceptions.py` -- Full exception hierarchy for cache error handling
- `backends/` -- Backend implementations: `in_memory.py`, `file_based.py`, `redis_backend.py`
- `policies/` -- Eviction policy implementations
- `invalidation/` -- Invalidation strategy implementations
- `distributed/` -- Distributed cache coordination
- `serializers/` -- Value serializer implementations
- `warmers/` -- Cache warming utilities
- `async_ops/` -- Async cache operation wrappers
- `replication/` -- Cache replication logic

## Quick Start

```python
from codomyrmex.cache import get_cache

result = get_cache()
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cache -v
```

## Navigation

- **Full Documentation**: [docs/modules/cache/](../../../docs/modules/cache/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
