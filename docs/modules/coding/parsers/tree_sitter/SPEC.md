# Tree-sitter — Functional Specification

**Module**: `codomyrmex.tree_sitter`  
**Version**: v1.0.0  
**Status**: Active

## 1. Overview

Tree-sitter parsing module for Codomyrmex.

## 2. Architecture

### Submodule Structure

- `languages/` — Language support submodule.
- `parsers/` — Tree-sitter parser utilities.
- `queries/` — Query building submodule.
- `transformers/` — AST transformers submodule.

## 3. Dependencies

See `src/codomyrmex/tree_sitter/__init__.py` for import dependencies.

## 4. Public API

See source module for available exports.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k tree_sitter -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/tree_sitter/)
