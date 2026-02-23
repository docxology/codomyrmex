# cache/invalidation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Cache invalidation strategies and policies. Provides a thread-safe `InvalidationManager` that supports TTL-based, LRU, LFU, FIFO, tag-based, and version-based invalidation. Cache entries track creation time, last access, access count, TTL, and tags. The manager maintains a tag index for bulk invalidation and a version registry for namespace-scoped cache busting.

## Key Exports

### Enums

- **`InvalidationStrategy`** -- Cache invalidation strategy enumeration (TTL, LRU, LFU, FIFO, TAG_BASED, VERSION_BASED)

### Data Classes

- **`CacheEntry`** -- Cache entry with metadata including key, value, timestamps, access_count, ttl_seconds, tags, and version; exposes `is_expired` property and `touch()` method

### Policies (Abstract + Implementations)

- **`InvalidationPolicy`** -- ABC defining `should_evict(entry)` and `select_for_eviction(entries)` interface
- **`TTLPolicy`** -- Time-to-live based invalidation with configurable default TTL
- **`LRUPolicy`** -- Least recently used invalidation; selects entry with oldest `last_accessed` timestamp
- **`LFUPolicy`** -- Least frequently used invalidation; selects entry with lowest `access_count`
- **`FIFOPolicy`** -- First-in-first-out invalidation; selects entry with oldest `created_at` timestamp

### Manager

- **`InvalidationManager`** -- Core manager with `set()`, `get()`, `invalidate()`, `invalidate_by_tag()`, `invalidate_all()`, version management (`set_version`, `get_version`, `increment_version`), and `stats()`

## Directory Contents

- `__init__.py` - Package init; contains all invalidation classes inline (single-file module)
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [cache](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
