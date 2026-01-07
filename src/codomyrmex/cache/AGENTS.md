# Codomyrmex Agents — src/codomyrmex/cache

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [backends](backends/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Unified caching strategies for code analysis results, LLM responses, build artifacts, and other frequently accessed data. Provides provider-agnostic caching interface with support for multiple backends (Redis, in-memory, file-based) with TTL support, statistics, and pattern-based invalidation.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `backends/` – Directory containing cache backend implementations (in_memory, file_based, redis_backend)
- `cache.py` – Abstract base cache interface
- `cache_manager.py` – Manager for cache instances
- `stats.py` – Cache statistics data structures

## Key Classes and Functions

### Cache (`cache.py`)
- `Cache` (ABC) – Abstract base class for cache implementations
- `get(key: str) -> Optional[Any]` – Get a value from the cache
- `set(key: str, value: Any, ttl: Optional[int] = None) -> bool` – Set a value in the cache with optional TTL
- `delete(key: str) -> bool` – Delete a key from the cache
- `clear() -> bool` – Clear all entries from the cache
- `exists(key: str) -> bool` – Check if a key exists in the cache
- `get_stats() -> CacheStats` – Get cache statistics
- `delete_pattern(pattern: str) -> int` – Delete all keys matching a pattern (supports wildcards)

### CacheManager (`cache_manager.py`)
- `CacheManager()` – Manager for cache instances
- `get_cache(name: str = "default", backend: Optional[str] = None) -> Cache` – Get a cache instance by name and backend (in_memory, file_based, redis)

### CacheStats (`stats.py`)
- `CacheStats` (dataclass) – Cache statistics:
  - `hits: int` – Number of cache hits
  - `misses: int` – Number of cache misses
  - `total_requests: int` – Total cache requests
  - `size: int` – Current cache size
  - `max_size: int` – Maximum cache size
- `hit_rate: float` (property) – Calculate hit rate
- `miss_rate: float` (property) – Calculate miss rate
- `usage_percent: float` (property) – Calculate cache usage percentage

### Cache Backends (`backends/`)
- `InMemoryCache` – In-memory cache implementation
- `FileBasedCache` – File-based cache implementation
- `RedisCache` – Redis cache implementation (requires redis package)

### Module Functions (`__init__.py`)
- `get_cache(name: str = "default", backend: str = "in_memory") -> Cache` – Get a cache instance

### Exceptions
- `CacheError` – Raised when cache operations fail

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation