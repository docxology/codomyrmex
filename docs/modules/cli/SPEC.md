# CLI — Functional Specification

**Module**: `codomyrmex.cli`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

This module provides the command-line interface for the Codomyrmex development platform.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|

### Submodule Structure

- `completions/` — Shell Completions submodule.
- `formatters/` — CLI Output Formatters.
- `handlers/` — CLI command handlers.
- `parsers/` — Argument Parsers submodule.
- `themes/` — CLI Themes submodule.

### Source Files

- `__main__.py`
- `core.py`
- `utils.py`

## 3. Dependencies

See `src/codomyrmex/cli/__init__.py` for import dependencies.

## 4. Public API

See source module for available exports.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cli -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/cli/)
