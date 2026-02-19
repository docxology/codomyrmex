# Documentation — Functional Specification

**Module**: `codomyrmex.documentation`  
**Version**: v0.1.7  
**Status**: Active

## 1. Overview

Documentation Module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|

### Submodule Structure

- `scripts/` — Documentation generation scripts.

### Source Files

- `consistency_checker.py`
- `documentation_website.py`
- `quality_assessment.py`

## 3. Dependencies

See `src/codomyrmex/documentation/__init__.py` for import dependencies.

## 4. Public API

See source module for available exports.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k documentation -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/documentation/)
