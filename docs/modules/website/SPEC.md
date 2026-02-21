# Website — Functional Specification

**Module**: `codomyrmex.website`  
**Version**: v1.0.0  
**Status**: Active

## 1. Overview

Website generation module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|

### Source Files

- `data_provider.py`
- `generator.py`
- `server.py`

## 3. Dependencies

See `src/codomyrmex/website/__init__.py` for import dependencies.

## 4. Public API

See source module for available exports.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k website -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/website/)
