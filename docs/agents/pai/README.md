# PAI Bridge

**Module**: `codomyrmex.agents.pai` | **Category**: Core Infrastructure | **Last Updated**: March 2026

## Overview

Comprehensive integration between Codomyrmex and the Personal AI Infrastructure (PAI). Provides MCP bridge exposing all Codomyrmex modules to PAI, trust-gated tool access, and programmatic access to all PAI subsystems — Algorithm, Skills, Tools, Hooks, Agents, Memory, Security, TELOS, and Settings.

## Key Classes

| Class | Purpose |
|:---|:---|
| `PAIBridge` | Main bridge connecting Codomyrmex to PAI |
| `PAIConfig` | Configuration for PAI integration |
| `call_tool(name)` | MCP tool invocation |
| `create_codomyrmex_mcp_server()` | Create MCP server exposing all modules |
| `verify_capabilities()` | Verify available MCP tools |
| `trust_all()` | Grant trust to all discoverable tools |

## Configuration

**Optional**: PAI installation at https://github.com/danielmiessler/Personal_AI_Infrastructure

## Usage

```python
from codomyrmex.agents.pai import PAIBridge

client = PAIBridge()
```

## Source Module

Source: [`src/codomyrmex/agents/pai/`](../../../src/codomyrmex/agents/pai/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/pai/](../../../src/codomyrmex/agents/pai/)
- **Project Root**: [README.md](../../../README.md)
