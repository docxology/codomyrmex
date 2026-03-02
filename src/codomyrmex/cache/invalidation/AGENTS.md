# Codomyrmex Agents — src/codomyrmex/cache/invalidation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Cache invalidation with pluggable eviction policies (TTL, LRU, LFU, FIFO), tag-based bulk invalidation, version-based namespace invalidation, and thread-safe cache operations with capacity management.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `InvalidationManager` | Thread-safe cache with pluggable policy, tag index, version namespaces, and capacity eviction |
| `__init__.py` | `InvalidationPolicy` (ABC) | Abstract base for eviction policies: `should_evict(entry)` and `select_for_eviction(entries)` |
| `__init__.py` | `TTLPolicy` | Time-to-live eviction -- evicts entries past their TTL |
| `__init__.py` | `LRUPolicy` | Least recently used -- selects by `last_accessed` timestamp |
| `__init__.py` | `LFUPolicy` | Least frequently used -- selects by `access_count` |
| `__init__.py` | `FIFOPolicy` | First in, first out -- selects by `created_at` timestamp |
| `__init__.py` | `CacheEntry` | Entry dataclass with key, value, timestamps, access_count, TTL, tags, version |
| `__init__.py` | `InvalidationStrategy` | Enum of strategy types: TTL, LRU, LFU, FIFO, TAG_BASED, VERSION_BASED |

## Operating Contracts

- `InvalidationManager` is thread-safe via `threading.Lock` on all mutating operations.
- Capacity eviction runs before `set()` inserts when cache is at `max_size`.
- Tag-based invalidation removes all entries sharing a tag via reverse index.
- Version-based invalidation uses namespace version counters (callers check version on read).
- `CacheEntry.touch()` updates `last_accessed` and increments `access_count` on every `get()`.
- Errors must be logged before re-raising.

## Integration Points

- **Depends on**: Standard library only (`threading`, `hashlib`, `time`, `dataclasses`)
- **Used by**: `cache` parent module, `cache.cache_manager`, `cache.namespaced`

## Navigation

- **Parent**: [cache](../README.md)
- **Root**: [Root](../../../../README.md)
