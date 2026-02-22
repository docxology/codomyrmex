# Personal AI Infrastructure — Static Analysis Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Static analysis utilities for imports and exports. This is a **Core Layer** module.

## PAI Capabilities

```python
from codomyrmex.static_analysis import scan_imports, check_layer_violations, extract_imports_ast
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `scan_imports` | Function/Constant | Scan imports |
| `check_layer_violations` | Function/Constant | Check layer violations |
| `extract_imports_ast` | Function/Constant | Extract imports ast |
| `audit_exports` | Function/Constant | Audit exports |
| `check_all_defined` | Function/Constant | Check all defined |

## PAI Algorithm Phase Mapping

| Phase | Static Analysis Contribution |
|-------|------------------------------|
| **VERIFY** | Validation and quality checks |

## Architecture Role

**Core Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
