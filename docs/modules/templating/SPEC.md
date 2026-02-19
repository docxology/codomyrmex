# Templating — Functional Specification

**Module**: `codomyrmex.templating`  
**Version**: v0.1.7  
**Status**: Active

## 1. Overview

Templating module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `TemplatingError` | Class | Raised when templating operations fail. |
| `get_default_engine()` | Function | Get or create default template engine instance. |
| `render()` | Function | Render a template string with context data. |
| `render_file()` | Function | Load and render a template file. |

### Submodule Structure

- `context/` — Context builders submodule.
- `engines/` — Template engine implementations.
- `filters/` — Template filters submodule.
- `loaders/` — Template loaders submodule.

## 3. Dependencies

See `src/codomyrmex/templating/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.templating import TemplatingError
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k templating -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/templating/)
