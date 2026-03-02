# Performance Caching -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Two-tier caching system providing both in-memory (with LRU eviction) and disk-based (pickle) persistence for memoizing expensive computations. Includes a decorator for transparent function-level caching.

## Architecture

`CacheManager` maintains an in-memory dict of `(value, timestamp, ttl)` tuples and mirrors entries to `.pkl` files on disk. Reads check memory first, then disk; expired entries are evicted on access. LRU eviction uses a parallel `_access_times` dict to find and remove the oldest entry when `max_memory_items` is exceeded.

## Key Classes

### `CacheManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `cache_dir: str\|Path\|None, max_memory_items: int=1000, default_ttl: int=3600` | `None` | Initialize with optional disk dir (defaults to temp), size limit, and TTL |
| `get` | `key: str` | `Any\|None` | Retrieve value; checks memory then disk; evicts expired entries |
| `set` | `key: str, value: Any, ttl: int\|None` | `None` | Store value in both tiers; triggers LRU eviction if over limit |
| `clear` | | `None` | Remove all in-memory entries and all `.pkl` files |
| `get_stats` | | `dict[str, Any]` | Returns memory_items, max_memory_items, cache_dir, disk_files |

### `cached_function` (decorator factory)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ttl` | `int\|None` | `None` | Per-entry TTL in seconds |
| `cache_key_prefix` | `str\|None` | `None` | Override function name in cache key |
| `cache_manager` | `CacheManager\|None` | `None` | Override global cache instance |

The decorated function gains `cache_clear()` and `cache_stats()` helper methods.

### Module-level Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `clear_cache()` | `None` | Clear the global singleton cache |
| `get_cache_stats()` | `dict` | Stats from the global singleton cache |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`
- **External**: `hashlib`, `json`, `pickle`, `tempfile`, `functools` (stdlib)

## Constraints

- Cache keys are MD5 hashes of JSON-serialized `(func_name, args, sorted_kwargs)`.
- Disk write failures are logged at debug level but do not propagate; the in-memory entry remains.
- Corrupted pickle files are silently deleted on read; a cache miss is returned.
- `_is_expired` uses `time.time()` for wall-clock TTL checks.
- Zero-mock: real file I/O only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `pickle.PickleError`, `EOFError`, `OSError` during disk reads are caught and the cache file is removed.
- `OSError`, `pickle.PickleError` during disk writes are caught and logged at debug level.
- All errors logged before propagation.
