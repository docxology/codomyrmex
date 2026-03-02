# Personal AI Infrastructure — Tree Sitter Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

Tree-sitter parsing module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.coding.parsers.tree_sitter import TreeSitterParser, LanguageManager, parsers, languages, queries
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `TreeSitterParser` | Class | Treesitterparser |
| `LanguageManager` | Class | Languagemanager |
| `parsers` | Function/Constant | Parsers |
| `languages` | Function/Constant | Languages |
| `queries` | Function/Constant | Queries |
| `transformers` | Function/Constant | Transformers |

## PAI Algorithm Phase Mapping

| Phase | Tree Sitter Contribution |
|-------|------------------------------|
| **EXECUTE** | General module operations |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.tree_sitter import ...`
- CLI: `codomyrmex tree_sitter <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../../PAI.md](../../PAI.md) — Coding module PAI
- **Root Bridge**: [../../../../../PAI.md](../../../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
