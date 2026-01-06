# Codomyrmex Agents — src/codomyrmex/cache

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Cache Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Purpose

Caching module providing unified caching strategies for code analysis results, LLM responses, build artifacts, and other frequently accessed data. This module integrates with the `performance` module to optimize platform responsiveness and reduce redundant computations.

The cache module serves as the caching layer, providing multiple backend options with a unified interface for consistent caching across the platform.

## Module Overview

### Key Capabilities
- **Multi-Backend Support**: Redis, in-memory, and file-based caching
- **Unified Interface**: Provider-agnostic caching API
- **TTL Management**: Configurable time-to-live for cache entries
- **Statistics Tracking**: Hit/miss rates and performance metrics
- **Serialization**: Automatic serialization/deserialization

### Key Features
- Backend-agnostic cache interface
- Support for multiple cache backends
- Configurable TTL and expiration
- Cache statistics and monitoring
- Pattern-based cache invalidation

## Function Signatures

### Core Cache Operations

```python
def get(key: str) -> Optional[Any]
```

Get a value from the cache.

**Parameters:**
- `key` (str): Cache key

**Returns:** `Optional[Any]` - Cached value if found, None otherwise

```python
def set(key: str, value: Any, ttl: Optional[int] = None) -> bool
```

Set a value in the cache with optional TTL.

**Parameters:**
- `key` (str): Cache key
- `value` (Any): Value to cache
- `ttl` (Optional[int]): Time-to-live in seconds

**Returns:** `bool` - True if successful

```python
def delete(key: str) -> bool
```

Delete a key from the cache.

**Parameters:**
- `key` (str): Cache key to delete

**Returns:** `bool` - True if deleted, False if key didn't exist

```python
def clear() -> bool
```

Clear all entries from the cache.

**Returns:** `bool` - True if successful

```python
def exists(key: str) -> bool
```

Check if a key exists in the cache.

**Parameters:**
- `key` (str): Cache key to check

**Returns:** `bool` - True if key exists

### Statistics Functions

```python
def get_stats() -> CacheStats
```

Get cache statistics including hit/miss rates.

**Returns:** `CacheStats` - Statistics object with hit_rate, miss_rate, total_requests, etc.

### Pattern Operations

```python
def delete_pattern(pattern: str) -> int
```

Delete all keys matching a pattern.

**Parameters:**
- `pattern` (str): Pattern to match (supports wildcards)

**Returns:** `int` - Number of keys deleted

### Cache Manager Functions

```python
def get_cache(name: str = "default", backend: str = None) -> Cache
```

Get a cache instance by name.

**Parameters:**
- `name` (str): Cache name
- `backend` (str): Optional backend override

**Returns:** `Cache` - Cache instance

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `cache.py` – Base cache interface
- `cache_manager.py` – Cache manager for multiple backends
- `backends/` – Backend implementations
  - `in_memory.py` – In-memory cache backend
  - `file_based.py` – File-based cache backend
  - `redis_backend.py` – Redis cache backend

### Documentation
- `README.md` – Module usage and overview
- `AGENTS.md` – This file: agent documentation
- `SPEC.md` – Functional specification

## Operating Contracts

### Universal Cache Protocols

All caching operations within the Codomyrmex platform must:

1. **Serialization Safety** - All cached values must be serializable
2. **TTL Enforcement** - Respect TTL settings and expire entries
3. **Error Handling** - Handle cache failures gracefully without breaking operations
4. **Statistics Collection** - Track cache performance metrics
5. **Thread Safety** - Support concurrent access where applicable

### Integration Guidelines

When integrating with other modules:

1. **Use Performance Module** - Integrate with performance monitoring
2. **Log Operations** - Log cache operations via logging_monitoring
3. **Configuration** - Use config_management for cache configuration
4. **Error Recovery** - Implement fallback when cache is unavailable

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Related Modules**:
    - [performance](../performance/AGENTS.md) - Performance monitoring
    - [config_management](../config_management/AGENTS.md) - Configuration management

