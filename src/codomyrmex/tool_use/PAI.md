# Personal AI Infrastructure — Tool Use Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Tool Use Module This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.tool_use import ValidationResult, ToolEntry, ToolRegistry, validate_input, validate_output, tool
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `ValidationResult` | Class | Validationresult |
| `validate_input` | Function/Constant | Validate input |
| `validate_output` | Function/Constant | Validate output |
| `ToolEntry` | Class | Toolentry |
| `ToolRegistry` | Class | Toolregistry |
| `tool` | Function/Constant | Tool |
| `ChainStep` | Class | Chainstep |
| `ChainResult` | Class | Chainresult |
| `ToolChain` | Class | Toolchain |

## PAI Algorithm Phase Mapping

| Phase | Tool Use Contribution |
|-------|------------------------------|
| **VERIFY** | Validation and quality checks |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
