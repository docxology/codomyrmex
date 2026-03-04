# Agent Guidelines - Cache

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Multi-backend in-process caching with memory, Redis, and disk backends. Provides a `CacheManager` singleton with named caches, TTL support, LRU eviction, hit/miss statistics, and a `@cached` decorator. Sprint 17 added four MCP tools for cache operations. Use for memoizing expensive computations, session data, and pipeline intermediate results.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `CacheManager`, `MemoryCache`, `RedisCache`, `DiskCache`, `cached` |
| `backends/` | Backend implementations (memory, redis, disk) |
| `policies/` | Eviction policies (LRU, LFU, TTL) |
| `mcp_tools.py` | MCP tools: `cache_get`, `cache_set`, `cache_delete`, `cache_stats` |

## Key Classes

- **`CacheManager`** — Singleton managing named cache instances
- **`MemoryCache`** — In-memory LRU cache with TTL and stats
- **`RedisCache`** — Redis-backed distributed cache (requires `redis` package)
- **`DiskCache`** — Filesystem-backed persistent cache

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `cache_get` | Get a value from the named in-memory cache. Returns value or None. | SAFE |
| `cache_set` | Store a value in the named cache with optional TTL in seconds. | SAFE |
| `cache_delete` | Delete a key from the named cache. Returns True if deleted. | SAFE |
| `cache_stats` | Get hit/miss/eviction statistics for a named cache. Returns hits, misses, hit_rate, size. | SAFE |

## Agent Instructions

1. **Set TTL** — Always set TTL to prevent unbounded growth; default TTL is no expiry
2. **Key naming** — Use consistent namespaced keys: `"module:type:identifier"`
3. **Use `cache_stats`** — Monitor hit rate to validate caching effectiveness
4. **Invalidate on mutation** — Delete cached entries when underlying data changes
5. **Module-level singleton** — Use `CacheManager()` singleton; multiple instantiations share state

## Common Patterns

```python
from codomyrmex.cache import MemoryCache, RedisCache, cached

# In-memory cache
cache = MemoryCache(max_size=1000)
cache.set("user:123", user_data, ttl=300)
user = cache.get("user:123")

# Redis cache
redis_cache = RedisCache(url="redis://localhost:6379")
redis_cache.set("session:abc", session, ttl=3600)

# Decorator
@cached(ttl=60)
def expensive_query(query):
    return db.execute(query)

# Batch operations
cache.set_many({
    "key1": value1,
    "key2": value2,
}, ttl=300)

# Invalidation
cache.delete("user:123")
cache.delete_pattern("user:*")  # All user keys
```

## Testing Patterns

```python
# Verify set/get
cache = MemoryCache()
cache.set("key", "value", ttl=60)
assert cache.get("key") == "value"

# Verify expiration
cache.set("temp", "data", ttl=0.1)
time.sleep(0.2)
assert cache.get("temp") is None

# Verify decorator
@cached(ttl=60)
def add(a, b):
    return a + b
assert add(1, 2) == 3
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `cache_get`, `cache_set`, `cache_delete`, `cache_stats` | TRUSTED |
| **Architect** | Read + Design | `cache_stats` — review cache effectiveness | OBSERVED |
| **QATester** | Validation | `cache_get`, `cache_stats` — verify hit/miss behavior | OBSERVED |
| **Researcher** | Read-only | `cache_get`, `cache_stats` — read cached results during analysis | SAFE |

### Engineer Agent
**Use Cases**: Configuring caches during BUILD, implementing cache warm-up during EXECUTE, tuning TTL settings.

### Architect Agent
**Use Cases**: Designing caching strategies, reviewing TTL policies, assessing hit rates.

### QATester Agent
**Use Cases**: Testing cache hit/miss behavior during VERIFY, confirming TTL-based invalidation.

### Researcher Agent
**Use Cases**: Reading cached results for research continuity, checking cache statistics.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/cache.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/cache.cursorrules)
