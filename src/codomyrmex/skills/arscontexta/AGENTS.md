# Agent Integration — Ars Contexta

Guidelines for PAI agents consuming Ars Contexta capabilities.

## Agent Type Mapping

| PAI Agent Type | Ars Contexta Service | Use Case |
|---------------|---------------------|----------|
| **Engineer** | `ArsContextaManager.setup()` | Build vault infrastructure |
| **Architect** | `KernelPrimitiveRegistry`, `DerivationEngine` | Design vault configuration |
| **Algorithm** | `MethodologyGraph` | ISC pressure-testing with research claims |
| **Researcher** | `MethodologyGraph.get_by_domain()` | Literature grounding |

## Delegation Patterns

### Single-Agent (Standard effort)

```
Agent receives vault_path → setup() → health() → return config
```

### Multi-Agent (Extended+ effort)

```
Architect: derive_config(user_text) → select primitives → design vault layout
Engineer:  setup(vault_path) → create templates → validate structure
Algorithm: methodology.get_related() → pressure-test ISC against research
```

## Tool Access

All 6 MCP tools are safe (read/create only, no destructive operations).
No trust gateway gating required.

## Context Requirements

When delegating to agents, include:
1. **vault_path** — target filesystem path
2. **user_text** — raw user preferences for derivation
3. **effort_level** — determines pipeline depth
