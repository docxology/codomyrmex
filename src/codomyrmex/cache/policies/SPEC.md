# Eviction Policies — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Generic, thread-safe cache eviction policies with pluggable strategy pattern. Each policy manages its own internal storage and provides a uniform get/put/remove/clear/size API.

## Architecture

Abstract `EvictionPolicy[K, V]` base class with four concrete implementations. Each maintains its own data structures optimized for the eviction strategy. All operations are protected by `threading.RLock`.

## Key Classes

### `EvictionPolicy[K, V]` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get` | `key: K` | `V \| None` | Retrieve value; removes if expired |
| `put` | `key: K, value: V, ttl: timedelta \| None` | `None` | Store value; evicts if at capacity |
| `remove` | `key: K` | `V \| None` | Remove and return value |
| `clear` | none | `None` | Clear all entries |
| `size` | none | `int` | Current entry count |
| `contains` | `key: K` | `bool` | Check existence (calls `get`) |

### `LRUPolicy`

- Storage: `OrderedDict[K, CacheEntry[V]]`
- On `get()`: moves key to end (most recently used)
- On capacity overflow: `popitem(last=False)` removes least recently used

### `LFUPolicy`

- Storage: `dict[K, CacheEntry[V]]` + `dict[int, OrderedDict[K, None]]` frequency map
- Tracks `_min_freq` for O(1) eviction of least frequently used key
- `_update_frequency` migrates key between frequency buckets on access

### `TTLPolicy`

- Storage: `dict[K, CacheEntry[V]]` + `heapq` expiry heap
- `_cleanup_expired()` runs on every `get()` and `put()` call
- Default TTL: 1 hour (`timedelta(hours=1)`)

### `FIFOPolicy`

- Storage: `OrderedDict[K, CacheEntry[V]]`
- On capacity overflow: `popitem(last=False)` removes oldest insertion

### `create_policy` (factory)

```python
create_policy(policy_name: str, max_size: int, **kwargs) -> EvictionPolicy
```

Accepted names: `"lru"`, `"lfu"`, `"ttl"`, `"fifo"`. Raises `ValueError` for unknown names.

## Dependencies

- **Internal**: None
- **External**: Standard library (`threading`, `heapq`, `collections.OrderedDict`, `datetime`, `dataclasses`)

## Constraints

- Thread-safe via `RLock` (reentrant); safe for same-thread recursive access.
- `CacheEntry.is_expired()` uses `datetime.now()` comparison; not monotonic-clock based.
- `LFUPolicy` frequency starts at 0; first `touch()` moves to 1.
- Zero-mock: real cache operations only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Expired entries are silently removed on `get()` and return `None`.
- `create_policy` raises `ValueError` for unknown policy names.
