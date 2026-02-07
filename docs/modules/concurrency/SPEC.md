# Concurrency — Functional Specification

**Module**: `codomyrmex.concurrency`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Concurrency and synchronization module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|

### Source Files

- `distributed_lock.py`
- `lock_manager.py`
- `redis_lock.py`
- `semaphore.py`

## 3. Dependencies

See `src/codomyrmex/concurrency/__init__.py` for import dependencies.

## 4. Public API

See source module for available exports.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k concurrency -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/concurrency/)
