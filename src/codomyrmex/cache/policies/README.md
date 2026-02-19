# cache/policies

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Cache eviction policies. Provides generic, thread-safe eviction policy implementations for use when cache capacity is reached. Each policy is a self-contained cache with `get`, `put`, `remove`, `clear`, and `size` operations. Supports LRU (OrderedDict-backed), LFU (frequency map with min-frequency tracking), TTL (heap-based lazy expiration), and FIFO (insertion-order) strategies. All policies are generic over key and value types.

## Key Exports

### Data Classes

- **`CacheEntry[V]`** -- Generic cache entry with value, timestamps (created_at, accessed_at), access_count, optional TTL, and size; provides `is_expired()` and `touch()` methods

### Abstract Base

- **`EvictionPolicy[K, V]`** -- Generic ABC defining `get(key)`, `put(key, value, ttl)`, `remove(key)`, `clear()`, `size()`, and `contains(key)` interface; thread-safe via `RLock`

### Policy Implementations

- **`LRUPolicy`** -- Least Recently Used eviction using `OrderedDict` for O(1) access reordering
- **`LFUPolicy`** -- Least Frequently Used eviction with frequency map and min-frequency tracker
- **`TTLPolicy`** -- TTL-based eviction with configurable default TTL and heap-based lazy cleanup of expired entries
- **`FIFOPolicy`** -- First In First Out eviction using `OrderedDict` insertion order

### Factory

- **`create_policy()`** -- Factory function to create eviction policies by name string ("lru", "lfu", "ttl", "fifo") with max_size and optional kwargs

## Directory Contents

- `__init__.py` - Package init; contains all eviction policy classes inline (single-file module)
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [cache](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
