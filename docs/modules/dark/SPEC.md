# Dark — Functional Specification

**Module**: `codomyrmex.dark`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Dark modes module - network, hardware, software, PDF dark mode utilities.

## 2. Architecture

### Submodule Structure

- `hardware/` — Dark mode utilities for hardware. (Not yet implemented)
- `network/` — Dark mode utilities for network. (Not yet implemented)
- `pdf/` — PDF dark mode filters inspired by dark-pdf.
- `software/` — Dark mode utilities for software. (Not yet implemented)

## 3. Dependencies

See `src/codomyrmex/dark/__init__.py` for import dependencies.

## 4. Public API

See source module for available exports.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k dark -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/dark/)
