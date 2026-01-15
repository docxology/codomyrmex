# Cache Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Cache module provides unified caching strategies for Codomyrmex, supporting multiple backends and use cases including code analysis results, LLM responses, build artifacts, and other frequently accessed data.

## Key Features

- **Multiple Backends**: In-memory, file-based, and Redis caching
- **Cache Manager**: Centralized cache instance management
- **Statistics Tracking**: Hit rates, miss counts, and performance metrics
- **TTL Support**: Time-to-live expiration for cache entries
- **Namespace Isolation**: Separate caches for different use cases

## Quick Start

```python
from codomyrmex.cache import get_cache, Cache, CacheManager, CacheStats

# Get a cache instance
cache = get_cache(name="llm_responses", backend="in_memory")

# Store and retrieve data
cache.set("prompt_hash_123", {"response": "Hello world"}, ttl=3600)
result = cache.get("prompt_hash_123")

# Check if key exists
if cache.has("prompt_hash_123"):
    data = cache.get("prompt_hash_123")

# Delete entry
cache.delete("prompt_hash_123")

# Get cache statistics
stats = cache.stats()
print(f"Hit rate: {stats.hit_rate:.2%}")

# Use cache manager for multiple caches
manager = CacheManager()
code_cache = manager.get_cache("code_analysis", backend="file_based")
build_cache = manager.get_cache("build_artifacts", backend="in_memory")
```

## Core Classes

| Class | Description |
|-------|-------------|
| `Cache` | Core cache operations (get, set, delete, has) |
| `CacheManager` | Manages multiple cache instances by name |
| `CacheStats` | Statistics tracking (hits, misses, hit rate) |

## Backends

| Backend | Use Case |
|---------|----------|
| `in_memory` | Fast, ephemeral caching for session data |
| `file_based` | Persistent caching across process restarts |
| `redis` | Distributed caching for multi-process setups |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `get_cache(name, backend)` | Get or create a cache instance |

## Exceptions

| Exception | Description |
|-----------|-------------|
| `CacheError` | Cache operations failed |

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
