# Cache Invalidation — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Pluggable cache invalidation framework with four built-in eviction policies, tag-based bulk invalidation, and version-based namespace invalidation.

## Architecture

Strategy pattern: `InvalidationManager` delegates eviction decisions to an `InvalidationPolicy` implementation. Four policies are provided (TTL, LRU, LFU, FIFO). The manager maintains a tag reverse-index and namespace version counters alongside the cache entries.

## Key Classes

### `InvalidationManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `set` | `key, value, ttl, tags` | `None` | Store entry; evicts if at capacity |
| `get` | `key: str` | `Any \| None` | Retrieve entry; evicts if policy says so; calls `touch()` |
| `invalidate` | `key: str` | `bool` | Remove a specific entry |
| `invalidate_by_tag` | `tag: str` | `int` | Remove all entries with matching tag |
| `invalidate_all` | none | `int` | Clear entire cache |
| `set_version` | `namespace: str, version: int` | `None` | Set namespace version |
| `increment_version` | `namespace: str` | `int` | Increment version (logical invalidation) |
| `stats` | none | `dict` | Cache size, max_size, tag count, namespace count |

Constructor: `policy: InvalidationPolicy | None = None` (default TTLPolicy), `max_size: int = 1000`

### `InvalidationPolicy` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `should_evict` | `entry: CacheEntry` | `bool` | Check if a specific entry should be evicted |
| `select_for_eviction` | `entries: dict[str, CacheEntry]` | `str \| None` | Select one entry key for eviction |

### Policy Implementations

| Policy | `should_evict` | `select_for_eviction` |
|--------|---------------|----------------------|
| `TTLPolicy` | True if entry past TTL | First expired entry |
| `LRUPolicy` | Always False | Entry with oldest `last_accessed` |
| `LFUPolicy` | Always False | Entry with lowest `access_count` |
| `FIFOPolicy` | Always False | Entry with oldest `created_at` |

## Dependencies

- **Internal**: None
- **External**: Standard library (`threading`, `hashlib`, `time`, `datetime`, `dataclasses`, `enum`)

## Constraints

- Thread-safe via `threading.Lock`; not async-safe.
- `max_size` eviction loop runs until capacity is available or no eviction candidate found.
- Version-based invalidation is logical: callers must compare versions on read.
- Zero-mock: real cache operations only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `get()` silently removes expired entries and returns `None`.
- No exceptions raised by invalidation operations; return counts or booleans.
