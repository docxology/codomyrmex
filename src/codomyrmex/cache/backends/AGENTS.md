# Codomyrmex Agents — src/codomyrmex/cache/backends

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Implements cache backend strategies for the cache module. Backends provide the underlying storage mechanisms for cached data, supporting in-memory, file-based, and Redis-backed caching with configurable TTL and eviction policies.

## Active Components

- `in_memory.py` - In-memory cache using Python dictionaries
- `file_based.py` - File-system backed cache with pickle serialization
- `redis_backend.py` - Redis-backed distributed cache
- `__init__.py` - Backend module initialization
- `SPEC.md` - Directory specification
- `README.md` - Directory documentation

## Key Classes and Functions

### in_memory.py
- **`InMemoryCache`** - Dictionary-based in-memory cache
  - `__init__(max_size, default_ttl)` - Initialize with size limit and TTL
  - `get(key)` - Retrieve value, checking expiration
  - `set(key, value, ttl)` - Store value with optional TTL
  - `delete(key)` - Remove entry
  - `clear()` - Remove all entries
  - `exists(key)` - Check existence with expiration
  - `stats` - Returns CacheStats object
  - `delete_pattern(pattern)` - Deletes keys matching fnmatch pattern

### file_based.py
- **`FileBasedCache`** - File-system persistent cache
  - `__init__(cache_dir, default_ttl)` - Initialize with directory and TTL
  - Uses MD5 hash of key for filenames
  - Stores metadata (timestamp, TTL) in separate .meta files
  - Values serialized with pickle

### redis_backend.py
- **`RedisCache`** - Redis-backed distributed cache
  - Supports Redis connection pooling
  - Native TTL support via Redis EXPIRE
  - Pattern-based key deletion with SCAN
  - Cluster-aware operations

### Cache Interface
All backends implement:
- `get(key) -> Optional[Any]`
- `set(key, value, ttl) -> bool`
- `delete(key) -> bool`
- `clear() -> bool`
- `exists(key) -> bool`
- `get_stats() -> CacheStats`

## Operating Contracts

- TTL in seconds (None = no expiration)
- Expired entries removed on access (lazy cleanup)
- In-memory cache uses LRU eviction when at max_size
- File-based cache creates directory if not exists
- Redis backend requires running Redis server
- All backends track hit/miss statistics

## Signposting

- **Dependencies**: `redis` package for RedisCache, `pickle` for serialization
- **Parent Directory**: [cache](../README.md) - Parent module documentation
- **Related Modules**:
  - `../cache.py` - Abstract Cache interface
  - `../stats.py` - CacheStats class
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
