# Personal AI Infrastructure — docs/pai Documentation Module

**Module**: docs/pai
**Version**: v0.4.0
**Status**: Active
**Upstream**: [danielmiessler/Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure)

## Context

This module provides the detailed reference layer in the PAI-Codomyrmex documentation hierarchy. It sits between the root bridge document (`/PAI.md`) and the implementation docs (`src/codomyrmex/agents/pai/`).

## Algorithm Phase Mapping

| Phase | Role |
|-------|------|
| **OBSERVE** | Read these docs to understand PAI-Codomyrmex integration |
| **THINK** | Use architecture.md to reason about system design |
| **PLAN** | Reference tools-reference.md and api-reference.md for implementation planning |
| **BUILD** | Use workflows.md for integration patterns |
| **VERIFY** | Cross-check counts against implementation |

## AI Strategy

1. **Start with README.md**: Index page links to all detailed documents
2. **Architecture first**: Understand the component model before diving into APIs
3. **Reference, not tutorial**: These docs explain what exists, not how to build it

## Signposting

### Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [docs/PAI.md](../PAI.md) — Documentation-level PAI index
- **Root Bridge**: [../../PAI.md](../../PAI.md) — Authoritative PAI system bridge

### Related Documentation

- [README.md](README.md) — Documentation index
- [AGENTS.md](AGENTS.md) — Agent coordination
- [SPEC.md](SPEC.md) — Functional specification
- [docs/modules/PAI.md](../modules/PAI.md) — Module-level AI agent context
- [architecture.md](architecture.md) — Architecture deep-dive
- [tools-reference.md](tools-reference.md) — Tool inventory
- [api-reference.md](api-reference.md) — Python API reference
- [workflows.md](workflows.md) — Workflow documentation
