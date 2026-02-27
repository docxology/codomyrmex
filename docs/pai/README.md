# PAI-Codomyrmex Integration Documentation

**Version**: v1.0.3-dev | **Status**: Active | **Last Updated**: February 2026

## Overview

This folder contains the detailed reference documentation for the PAI (Personal AI Infrastructure) integration within Codomyrmex. It expands on the [root PAI.md bridge document](../../PAI.md) with architecture deep-dives, complete tool inventories, and API references.

## Documentation Hierarchy

```
PAI.md (repo root)           → Bridge overview: what PAI is, how it connects
  └── docs/pai/ (this folder) → Detailed reference: architecture, tools, API
       └── src/codomyrmex/agents/pai/ → Implementation docs: RASP files alongside code
```

## Contents

| Document | Description |
|----------|-------------|
| [architecture.md](architecture.md) | MCP bridge architecture, trust model, data flow |
| [tools-reference.md](tools-reference.md) | All 20 static tools + dynamic discovery mechanism |
| [api-reference.md](api-reference.md) | Python API: PAIBridge, TrustRegistry, dataclasses |
| [workflows.md](workflows.md) | `/codomyrmexVerify`, `/codomyrmexTrust`, Algorithm mapping |

### RASP Documentation

| Document | Description |
|----------|-------------|
| [AGENTS.md](AGENTS.md) | Agent coordination for this documentation module |
| [SPEC.md](SPEC.md) | Functional specification |
| [PAI.md](PAI.md) | PAI integration metadata |

## Quick Links

- **Root bridge doc**: [`/PAI.md`](../../PAI.md)
- **Implementation**: [`src/codomyrmex/agents/pai/`](../../src/codomyrmex/agents/pai/)
- **MCP bridge code**: [`mcp_bridge.py`](../../src/codomyrmex/agents/pai/mcp_bridge.py)
- **Trust gateway code**: [`trust_gateway.py`](../../src/codomyrmex/agents/pai/trust_gateway.py)
- **PAI bridge code**: [`pai_bridge.py`](../../src/codomyrmex/agents/pai/pai_bridge.py)
- **PAI upstream**: [danielmiessler/Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure)

## Navigation

- **Self**: [README.md](README.md)
- **Parent**: [docs/](../) — Documentation hub
- **Root PAI Bridge**: [../../PAI.md](../../PAI.md)
- **Implementation**: [../../src/codomyrmex/agents/pai/](../../src/codomyrmex/agents/pai/)
