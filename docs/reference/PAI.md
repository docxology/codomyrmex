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
| --- | --- |
| `api.md` | API overview by module |
| `api-complete.md` | Detailed API reference |
| `cli.md` | CLI reference |
| `inventory.md` | Module and MCP tool inventory |

## PAI Integration

```python
from pathlib import Path

from codomyrmex.system_discovery import CapabilityScanner

# Query the API surface of a module (runtime import + AST introspection)
scanner = CapabilityScanner(Path("."))
api = scanner.scan_module("llm", Path("src/codomyrmex/llm"))
print([f.name for f in api.functions])
print([c.name for c in api.classes])
```

## Cross-References

- [README.md](README.md) — Overview
- [AGENTS.md](AGENTS.md) — Agent rules
- [SPEC.md](SPEC.md) — Specification
- [../](../) — Parent docs directory
