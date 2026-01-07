# backends

## Signposting
- **Parent**: [backends](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Cache backend implementations including in-memory, file-based, and Redis backends. Provides pluggable cache backends for different storage requirements and performance characteristics.

## Directory Contents
- `__init__.py` – File
- `file_based.py` – File
- `in_memory.py` – File
- `redis_backend.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [cache](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.cache.backends import InMemoryCache, FileBasedCache

# Use in-memory cache for fast access
memory_cache = InMemoryCache()
memory_cache.set("key1", "value1", ttl=300)
value = memory_cache.get("key1")

# Use file-based cache for persistence
file_cache = FileBasedCache(cache_dir="./cache")
file_cache.set("key2", {"data": "value"}, ttl=600)
cached_data = file_cache.get("key2")
```

