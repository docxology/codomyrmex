# Personal AI Infrastructure — Cache Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Cache module provides PAI integration for caching LLM responses and computed results.

## PAI Capabilities

### Response Caching

Cache LLM responses:

```python
from codomyrmex.cache import LLMCache

cache = LLMCache()

# Check cache first
cached = cache.get(prompt_hash)
if cached:
    return cached

# Store new response
cache.set(prompt_hash, response, ttl=3600)
```

### Multi-Backend

Use different cache backends:

```python
from codomyrmex.cache import MemoryCache, RedisCache

memory = MemoryCache(max_size=1000)
redis = RedisCache(url="redis://localhost")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `LLMCache` | Cache LLM responses |
| `MemoryCache` | In-memory caching |
| `RedisCache` | Distributed caching |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
