# Cache Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Cache module for Codomyrmex.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- `get_cache()` — Get a cache instance by name.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `async_ops` | Async Ops Submodule |
| `backends` | Cache backend implementations. |
| `distributed` | Distributed Cache submodule. |
| `invalidation` | Cache Invalidation Module |
| `policies` | Cache eviction policies. |
| `replication` | Replication Submodule |
| `serializers` | Cache serialization utilities. |
| `warmers` | Cache Warmers Module |

## Quick Start

```python
from codomyrmex.cache import get_cache

# Use the module
result = get_cache()
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cache -v
```

## Navigation

- **Source**: [src/codomyrmex/cache/](../../../src/codomyrmex/cache/)
- **Parent**: [Modules](../README.md)
