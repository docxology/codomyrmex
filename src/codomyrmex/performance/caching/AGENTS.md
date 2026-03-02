# Codomyrmex Agents -- src/codomyrmex/performance/caching

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides a two-tier caching system (in-memory with LRU eviction plus disk-based pickle persistence) for memoizing expensive computations across codomyrmex modules.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `cache_manager.py` | `CacheManager` | Two-tier cache with in-memory LRU and disk-based pickle storage, configurable TTL and size limits |
| `cache_manager.py` | `cached_function` | Decorator that auto-caches function results by hashing args/kwargs into an MD5 key |
| `cache_manager.py` | `clear_cache` | Clears all entries in the global cache manager |
| `cache_manager.py` | `get_cache_stats` | Returns statistics (memory items, disk files, limits) from the global cache |

## Operating Contracts

- `CacheManager.get` checks in-memory first, then disk; expired entries are evicted on access.
- `CacheManager.set` stores in both memory and disk; LRU eviction triggers when `max_memory_items` is exceeded.
- Cache keys are MD5 hashes of JSON-serialized function name, args, and kwargs.
- Disk cache uses Python `pickle`; corrupted or unreadable files are silently removed and cache miss is returned.
- Disk write failures are logged at debug level but do not raise; the in-memory copy remains valid.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring.core.logger_config`
- **Used by**: Any module needing memoization; a global `_cache_manager` singleton is available via `cached_function`, `clear_cache`, and `get_cache_stats`

## Navigation

- **Parent**: [performance](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
