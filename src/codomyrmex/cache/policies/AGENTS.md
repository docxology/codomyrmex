# Codomyrmex Agents — src/codomyrmex/cache/policies

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Self-contained cache eviction policies implementing get/put/remove/clear with thread-safe internal storage. Four policies are provided: LRU (OrderedDict), LFU (frequency map), TTL (heap-based lazy expiration), and FIFO (OrderedDict). A factory function creates policies by name.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `EvictionPolicy` (ABC, Generic) | Abstract base with `get`, `put`, `remove`, `clear`, `size` contract; thread-safe via `RLock` |
| `__init__.py` | `LRUPolicy` | Least recently used via `OrderedDict.move_to_end`; evicts first item |
| `__init__.py` | `LFUPolicy` | Least frequently used via frequency map with `OrderedDict` per frequency level |
| `__init__.py` | `TTLPolicy` | TTL-based with `heapq` expiry heap and lazy cleanup on access |
| `__init__.py` | `FIFOPolicy` | First in, first out via `OrderedDict.popitem(last=False)` |
| `__init__.py` | `CacheEntry` (Generic) | Entry dataclass with value, timestamps, access_count, TTL, and size |
| `__init__.py` | `create_policy` | Factory function: `create_policy("lru", max_size=100)` |

## Operating Contracts

- All policies are thread-safe via `threading.RLock`.
- `get()` returns `None` and removes the entry if it has expired.
- `put()` triggers eviction when cache is at `max_size`.
- `LFUPolicy` tracks minimum frequency to evict in O(1).
- `TTLPolicy` uses a `heapq` to efficiently find and remove expired entries on access.
- Errors must be logged before re-raising.

## Integration Points

- **Depends on**: Standard library only (`threading`, `heapq`, `collections.OrderedDict`, `dataclasses`)
- **Used by**: `cache` parent module, `cache.cache_manager`

## Navigation

- **Parent**: [cache](../README.md)
- **Root**: [Root](../../../../README.md)
