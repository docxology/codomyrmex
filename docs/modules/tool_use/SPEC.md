# Tool Use — Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.tool_use`  
**Status**: Active

## 1. Overview

Tool Use Module

Registry, composition, and validation for tool-based workflows.
Provides a central registry for managing tools, a chain abstraction
for sequential tool pipelines, and input/output validation utilities.

## 2. Architecture

### Source Files

| File | Purpose |
|------|--------|
| `chains.py` | Tool chain composition for sequential tool execution. |
| `registry.py` | Tool registry for managing available tools. |
| `validation.py` | Input/output validation for tool calls. |

## 3. Dependencies

No internal Codomyrmex dependencies.

## 4. Public API

### Exports (`__all__`)

- `ValidationResult`
- `validate_input`
- `validate_output`
- `ToolEntry`
- `ToolRegistry`
- `tool`
- `ChainStep`
- `ChainResult`
- `ToolChain`

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k tool_use -v
```

All tests follow the Zero-Mock policy.

## 6. References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Docs](../../../docs/modules/tool_use/)
