# Personal AI Infrastructure

**Module**: `codomyrmex.agents.pai` | **Category**: Core Infrastructure | **Last Updated**: March 2026

## Overview

Integration layer between agents and the Personal AI Infrastructure (PAI). Provides dashboard coordination, dual-interface orchestration (Python admin + Bun PM), and WebSocket push for real-time updates.

## Purpose

Comprehensive bridge to the PAI (Personal AI Infrastructure) system. Provides programmatic access to all PAI subsystems at `~/.claude/PAI/` (v4+; v3 legacy: `~/.claude/skills/PAI/`).

## Source Module Structure

Source: [`src/codomyrmex/agents/pai/`](../../../../src/codomyrmex/agents/pai/)

### Key Files

| File | Purpose |
|:---|:---|
| [_models.py](../../../../src/codomyrmex/agents/pai/_models.py) |  |
| [_modules.py](../../../../src/codomyrmex/agents/pai/_modules.py) |  |
| [_systems.py](../../../../src/codomyrmex/agents/pai/_systems.py) |  |
| [_verification.py](../../../../src/codomyrmex/agents/pai/_verification.py) |  |
| [mcp_bridge.py](../../../../src/codomyrmex/agents/pai/mcp_bridge.py) |  |
| [pai_bridge.py](../../../../src/codomyrmex/agents/pai/pai_bridge.py) |  ⭐ |
| [pai_client.py](../../../../src/codomyrmex/agents/pai/pai_client.py) |  |
| [pai_webhook.py](../../../../src/codomyrmex/agents/pai/pai_webhook.py) |  |
| [trust_gateway.py](../../../../src/codomyrmex/agents/pai/trust_gateway.py) |  |

### Subdirectories

- `mcp/`
- `pm/`

## Quick Start

```python
from codomyrmex.agents.pai import PaiClient

client = PaiClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [pai/README.md](../../../../src/codomyrmex/agents/pai/README.md) |
| SPEC | [pai/SPEC.md](../../../../src/codomyrmex/agents/pai/SPEC.md) |
| AGENTS | [pai/AGENTS.md](../../../../src/codomyrmex/agents/pai/AGENTS.md) |
| PAI | [pai/PAI.md](../../../../src/codomyrmex/agents/pai/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/pai/](../../../../src/codomyrmex/agents/pai/)
- **Project Root**: [README.md](../../../README.md)
