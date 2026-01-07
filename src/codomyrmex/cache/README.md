# cache

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [backends](backends/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Unified caching strategies for code analysis results, LLM responses, build artifacts, and other frequently accessed data. Provides provider-agnostic caching interface with support for multiple backends (Redis, in-memory, file-based) with TTL support, statistics tracking, and pattern-based invalidation.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `backends/` – Subdirectory
- `cache.py` – File
- `cache_manager.py` – File
- `stats.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.cache import get_cache, CacheManager

# Get a cache instance
cache = get_cache(name="my_cache", backend="in_memory")

# Basic operations
cache.set("key1", "value1", ttl=3600)
value = cache.get("key1")
exists = cache.exists("key1")
cache.delete("key1")

# Pattern-based deletion
deleted_count = cache.delete_pattern("prefix_*")

# Statistics
stats = cache.get_stats()
print(f"Hit rate: {stats.hit_rate}")
print(f"Usage: {stats.usage_percent}%")

# Using different backends
cache_manager = CacheManager()
redis_cache = cache_manager.get_cache("redis_cache", backend="redis")
file_cache = cache_manager.get_cache("file_cache", backend="file_based")
```

