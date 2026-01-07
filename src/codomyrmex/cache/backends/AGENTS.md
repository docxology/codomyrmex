# Codomyrmex Agents — src/codomyrmex/cache/backends

## Signposting
- **Parent**: [cache](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Cache backend implementations including in-memory, file-based, and Redis backends. Provides pluggable cache backends for different storage requirements and performance characteristics.

## Active Components
- `__init__.py` – Module exports and public API
- `file_based.py` – File-based cache backend
- `in_memory.py` – In-memory cache backend
- `redis_backend.py` – Redis cache backend

## Key Classes and Functions

### InMemoryBackend (`in_memory.py`)
- `InMemoryBackend()` – In-memory cache backend
- `get(key: str) -> Optional[Any]` – Get value from cache
- `set(key: str, value: Any, ttl: Optional[int] = None) -> None` – Set value in cache
- `delete(key: str) -> bool` – Delete value from cache
- `clear() -> None` – Clear all cache entries

### FileBasedBackend (`file_based.py`)
- `FileBasedBackend(cache_dir: str)` – File-based cache backend
- `get(key: str) -> Optional[Any]` – Get value from cache
- `set(key: str, value: Any, ttl: Optional[int] = None) -> None` – Set value in cache
- `delete(key: str) -> bool` – Delete value from cache
- `clear() -> None` – Clear all cache entries

### RedisBackend (`redis_backend.py`)
- `RedisBackend(redis_url: str)` – Redis cache backend
- `get(key: str) -> Optional[Any]` – Get value from cache
- `set(key: str, value: Any, ttl: Optional[int] = None) -> None` – Set value in cache
- `delete(key: str) -> bool` – Delete value from cache
- `clear() -> None` – Clear all cache entries

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [cache](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation