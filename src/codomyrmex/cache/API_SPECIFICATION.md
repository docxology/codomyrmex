# Cache Module API Specification

**Version**: v0.1.7 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview
The `cache` module provides a unified interface for data caching strategies in Codomyrmex. It supports ephemeral (in-memory) and persistent (file-based, Redis) caching backends to optimize performance for repeated operations like static analysis or LLM queries.

## 2. Core Components

### 2.1 Factory
- **`get_cache(name: str = "default", backend: str = "in_memory") -> Cache`**: Retrieves or creates a named cache instance.

### 2.2 Classes
- **`Cache` (Abstract Base)**: Defines the standard caching interface (`get`, `set`, `delete`, `clear`).
- **`CacheManager`**: Orchestrates multiple cache instances.
- **`CacheStats`**: Tracks hit/miss ratios and usage metrics.

## 3. Usage Example

```python
from codomyrmex.cache import get_cache

# Get a file-based cache
cache = get_cache("analysis_results", backend="file_based")

# Store data
cache.set("file_hash_123", {"complexity": 5})

# Retrieve data
result = cache.get("file_hash_123")
```
