# Agent Guidelines - Cache

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Multi-backend caching: memory, Redis, and disk.

## Key Classes

- **Cache** — Abstract cache interface
- **MemoryCache** — In-memory LRU cache
- **RedisCache** — Redis-backed cache
- **DiskCache** — Filesystem cache

## Agent Instructions

1. **Set TTL** — Always set expiration
2. **Key naming** — Use consistent key patterns
3. **Serialize** — Handle complex objects
4. **Invalidate** — Clear stale entries
5. **Monitor hits** — Track hit/miss ratio

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

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Cache read/write, TTL configuration, cache invalidation, warm-up strategies | TRUSTED |
| **Architect** | Read + Design | Caching strategy design, TTL policy review, cache topology planning | OBSERVED |
| **QATester** | Validation | Cache hit/miss verification, TTL behavior testing, invalidation correctness | OBSERVED |

### Engineer Agent
**Use Cases**: Configuring caches during BUILD, implementing cache warm-up during EXECUTE.

### Architect Agent
**Use Cases**: Designing caching strategies, reviewing TTL policies, planning cache hierarchies.

### QATester Agent
**Use Cases**: Testing cache hit/miss behavior during VERIFY, confirming invalidation logic.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
