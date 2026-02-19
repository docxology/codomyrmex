# Cerebrum — Functional Specification

**Module**: `codomyrmex.cerebrum`  
**Version**: v0.1.7  
**Status**: Active

## 1. Overview

CEREBRUM Module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|

### Submodule Structure

- `core/` — Core Cerebrum reasoning logic and engine.
- `fpf/` — First Principles Framework integration for Cerebrum.
- `inference/` — Inference mechanisms for Cerebrum.
- `visualization/` — Visualization tools for Cerebrum reasoning engine.

### Source Files

- `visualization_base.py`
- `visualization_theme.py`

## 3. Dependencies

See `src/codomyrmex/cerebrum/__init__.py` for import dependencies.

## 4. Public API

See source module for available exports.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cerebrum -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/cerebrum/)
