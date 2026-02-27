# docs/pai — Functional Specification

**Version**: v1.0.3-dev | **Status**: Active | **Last Updated**: February 2026

## Purpose

Expanded reference documentation for the PAI-Codomyrmex integration. Supplements the root `PAI.md` bridge document with detailed architecture, API, and tool references.

## Scope

| Document | Covers |
|----------|--------|
| `architecture.md` | Component diagram, data flow, trust model, cross-language communication |
| `tools-reference.md` | All 20 static tools with parameters, trust levels; dynamic discovery mechanism |
| `api-reference.md` | PAIBridge (24 methods), TrustRegistry, module functions, dataclasses, constants |
| `workflows.md` | `/codomyrmexVerify`, `/codomyrmexTrust`, Algorithm phase mapping |

## Design Principles

1. **Hierarchy**: Root PAI.md (bridge overview) → docs/pai/ (detailed reference) → src/ (implementation docs)
2. **No duplication**: Each document has a unique scope — no verbatim copying from root PAI.md
3. **Synchronized**: All counts (20 tools, 10 prompts, 2 resources, 4 destructive) match implementation

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Agent Documentation**: [AGENTS.md](AGENTS.md)
- **PAI Integration**: [PAI.md](PAI.md)
- **Parent**: [docs/](../)
