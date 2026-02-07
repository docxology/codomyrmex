# FPF (Filesystem Processing Framework) — Functional Specification

**Module**: `codomyrmex.fpf`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

First Principles Framework (FPF) module.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `FPFClient` | Class | High-level client for working with FPF specifications. |
| `load_from_file()` | Function | Load and parse FPF specification from a local file. |
| `fetch_and_load()` | Function | Fetch latest FPF specification from GitHub and load it. |
| `search()` | Function | Search for patterns. |
| `get_pattern()` | Function | Get a pattern by ID. |
| `export_json()` | Function | Export the specification to JSON. |

### Submodule Structure

- `constraints/` — Constraint Definitions submodule.
- `models/` — Domain Models submodule.
- `optimization/` — Constraint Optimization submodule.
- `reasoning/` — First Principles Framework reasoning utilities.

## 3. Dependencies

See `src/codomyrmex/fpf/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.fpf import FPFClient
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k fpf -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/fpf/)
