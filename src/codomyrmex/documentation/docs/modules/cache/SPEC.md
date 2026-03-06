# Cache -- Technical Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Cache Interface
- The `Cache` abstract base class shall define: `get(key)`, `set(key, value, ttl)`, `delete(key)`, `clear()`, `exists(key)`.
- All backends shall implement this interface.

### FR-2: Storage Backends
- In-memory backend: dictionary-based, volatile, fastest access.
- File-based backend: disk-persistent cache with serialization.
- Redis backend: distributed cache with network access.

### FR-3: Cache Manager
- `CacheManager` shall create and manage named cache instances.
- Cache instances shall be reusable across multiple get_cache() calls with the same name.

### FR-4: TTL Management
- `TTLManager` shall handle time-based expiration of cache entries.
- Expired entries shall be lazily evicted on access.

### FR-5: Namespace Isolation
- `NamespacedCache` shall prefix all keys with a namespace string.
- Namespaced operations shall be transparent to consumers.

### FR-6: Statistics
- `CacheStats` shall track: hits, misses, writes, deletes, evictions, current size.
- Hit rate shall be computed as hits / (hits + misses).

### FR-7: Eviction Policies
- The policies subpackage shall support LRU, LFU, and FIFO eviction strategies.

## Interface Contracts

### MCP Tool Signatures

```python
def cache_get(key: str, cache_name: str = "default") -> object | None
def cache_set(key: str, value: object, ttl: int | None = None, cache_name: str = "default") -> bool
def cache_delete(key: str, cache_name: str = "default") -> bool
def cache_stats(cache_name: str = "default") -> dict
```

### CacheManager Singleton
The MCP tools use a module-level `CacheManager` singleton so that data persists across multiple tool calls within the same process.

## Non-Functional Requirements

### NFR-1: Performance
- In-memory get/set/delete operations shall complete in O(1) amortized time.
- Cache statistics computation shall not add measurable overhead to cache operations.

### NFR-2: Thread Safety
- Cache operations shall be safe for concurrent access from multiple threads.

### NFR-3: Serialization
- Pluggable serializers (JSON, pickle, msgpack) shall be supported for value encoding.
- Serialization errors shall raise `CacheSerializationError`.

## Testing Requirements

- All tests follow the Zero-Mock policy.
- Tests use real cache instances with actual data storage and retrieval.
- TTL tests use real time delays (marked with `@pytest.mark.slow` if > 1 second).

## Navigation

- **Source**: [src/codomyrmex/cache/](../../../../src/codomyrmex/cache/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
