# Cache

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Cache module provides unified caching strategies for code analysis results, LLM responses, build artifacts, and other frequently accessed data within the codomyrmex platform. It features an abstract `Cache` interface with in-memory, file-based, and Redis backends; a `CacheManager` for named cache instance lifecycle; namespace isolation; TTL management; configurable eviction policies; invalidation strategies; pluggable serializers; distributed caching; cache warmers; replication; and async-compatible operations.

## Architecture Overview

The module is built around the `Cache` abstract base class, with `CacheManager` providing a factory and registry for named cache instances. Seven subpackages extend the core with specialized caching concerns (policies, invalidation, distributed, serializers, warmers, replication, async_ops).

```
cache/
├── __init__.py              # Public API (20+ exports, get_cache convenience function)
├── cache.py                 # Cache abstract base class
├── cache_manager.py         # CacheManager factory and registry
├── stats.py                 # CacheStats performance tracking
├── namespaced.py            # NamespacedCache key-prefix isolation
├── ttl_manager.py           # TTLManager for time-based expiration
├── exceptions.py            # Cache exception hierarchy (7 types)
├── mcp_tools.py             # MCP tools (cache_get, cache_set, cache_delete, cache_stats)
├── backends/                # Backend implementations (in_memory, file_based, redis)
├── policies/                # Eviction policy implementations (LRU, LFU, FIFO)
├── invalidation/            # Invalidation strategies (tag-based, pattern-based, event-driven)
├── distributed/             # Distributed cache coordination
├── serializers/             # Value serializers (JSON, pickle, msgpack)
├── warmers/                 # Cache warming utilities
├── async_ops/               # Async-compatible cache operations
└── replication/             # Cache replication across nodes
```

## PAI Integration

### Algorithm Phase Mapping

| Algorithm Phase | Role | Key Operations |
|----------------|------|---------------|
| OBSERVE | Check cached state to skip redundant data fetches | `cache_get` |
| BUILD | Cache intermediate computation results | `cache_set` |
| LEARN | Persist learned data and analysis results for reuse | `cache_set` with long TTL |

## Key Classes and Functions

### Core Classes

**`Cache`** -- Abstract base class defining the cache contract with `get()`, `set()`, `delete()`, `clear()`, and `exists()` methods.

**`CacheManager`** -- Factory and registry for named cache instances.

```python
from codomyrmex.cache import get_cache

cache = get_cache("my-cache", backend="in_memory")
cache.set("key", "value", ttl=300)
result = cache.get("key")
```

**`CacheStats`** -- Statistics tracker recording hits, misses, evictions, and size.

**`NamespacedCache`** -- Wraps a cache with key prefixes for consumer isolation.

**`TTLManager`** -- Manages time-to-live expiration for cache entries.

### Convenience Functions

**`get_cache(name, backend)`** -- Obtain a named cache instance via the CacheManager.

## MCP Tools Reference

| Tool | Description | Parameters | Trust Level |
|------|-------------|------------|-------------|
| `cache_get` | Get a value from the named cache | `key: str`, `cache_name: str = "default"` | Safe |
| `cache_set` | Store a value with optional TTL | `key: str`, `value: object`, `ttl: int | None`, `cache_name: str = "default"` | Safe |
| `cache_delete` | Delete a key from the cache | `key: str`, `cache_name: str = "default"` | Safe |
| `cache_stats` | Get hit/miss/eviction statistics | `cache_name: str = "default"` | Safe |

## Usage Examples

### Example 1: Basic Caching

```python
from codomyrmex.cache import get_cache

cache = get_cache("analysis")
cache.set("file_hash_abc123", {"complexity": 42, "lines": 150}, ttl=3600)
result = cache.get("file_hash_abc123")
```

### Example 2: Namespaced Isolation

```python
from codomyrmex.cache import get_cache, NamespacedCache

base_cache = get_cache("shared")
agent_cache = NamespacedCache(base_cache, namespace="agent_1")
agent_cache.set("context", {"task": "review"})
# Stored as "agent_1:context" in the underlying cache
```

## Error Handling

- `CacheError` -- Base exception for all cache-related errors
- `CacheExpiredError` -- Raised when accessing an entry that has exceeded its TTL
- `CacheFullError` -- Raised when the cache has reached its capacity limit
- `CacheConnectionError` -- Raised when connection to a remote cache backend fails
- `CacheKeyError` -- Raised for invalid or missing cache keys
- `CacheSerializationError` -- Raised when value serialization/deserialization fails
- `CacheInvalidationError` -- Raised when a cache invalidation operation fails

## Related Modules

- [`config_management`](../config_management/readme.md) -- Configuration that may be cached
- [`performance`](../performance/readme.md) -- Performance benchmarks that benefit from caching

## Navigation

- **Source**: [src/codomyrmex/cache/](../../../../src/codomyrmex/cache/)
- **API Spec**: [API_SPECIFICATION.md](../../../../src/codomyrmex/cache/API_SPECIFICATION.md)
- **Parent**: [All Modules](../README.md)
