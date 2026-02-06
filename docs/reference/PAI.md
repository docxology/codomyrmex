# Personal AI Infrastructure Context: docs/reference/

## Purpose

API reference documentation and technical specifications for all Codomyrmex modules.

## AI Agent Guidance

This directory contains API references. AI agents should:

1. **Look up APIs** — Find function signatures and parameters
2. **Check types** — Verify type annotations
3. **Find examples** — Use provided code examples

## Directory Structure

| File | Description |
|------|-------------|
| `api_index.md` | Index of all APIs |
| `type_reference.md` | Type definitions |
| `constants.md` | Global constants |
| `exceptions.md` | Exception types |

## PAI Integration

```python
from codomyrmex.system_discovery import get_api_reference

# Query API documentation
api = get_api_reference("codomyrmex.llm")
print(api.functions)
print(api.classes)
```

## Cross-References

- [README.md](README.md) — Overview
- [AGENTS.md](AGENTS.md) — Agent rules
- [SPEC.md](SPEC.md) — Specification
- [../](../) — Parent docs directory
