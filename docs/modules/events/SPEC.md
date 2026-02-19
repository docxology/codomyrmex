# Events — Functional Specification

**Module**: `codomyrmex.events`  
**Version**: v0.1.7  
**Status**: Active

## 1. Overview

Event-Driven Architecture for Codomyrmex

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|

### Source Files

- `emitter.py`
- `event_bus.py`
- `event_emitter.py`
- `event_listener.py`
- `event_logger.py`
- `event_schema.py`
- `exceptions.py`

## 3. Dependencies

See `src/codomyrmex/events/__init__.py` for import dependencies.

## 4. Public API

See source module for available exports.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k events -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/events/)
