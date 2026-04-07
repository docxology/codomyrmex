# Pi Coding Agent

**Module**: `codomyrmex.agents.pi` | **Category**: CLI-based | **Version**: v1.0.0 | **Last Updated**: March 2026

## Overview

Wraps the [Pi coding agent](https://pi.dev/) CLI for programmatic use via its RPC (JSON-over-stdin/stdout) protocol. Provides high-level task submission, project analysis, and code generation.

## Key Classes

| Class | Purpose |
|:---|:---|
| `PiClient` | High-level RPC client for the pi coding agent |
| `PiConfig` | Configuration dataclass |
| `PiError` | Exception hierarchy |

## Usage

```python
from codomyrmex.agents.pi import PiClient, PiConfig

client = PiClient(config=PiConfig(working_dir="/path/to/project"))
response = client.execute(AgentRequest(prompt="Analyze the parser module"))
```

## Configuration

**Required**: `pi` CLI installed via npm.

```bash
npm install -g @anthropic/pi-coding-agent
```

## Source Module

Source: [`src/codomyrmex/agents/pi/`](../../../src/codomyrmex/agents/pi/)

| File | Purpose |
|:---|:---|
| `pi_client.py` | RPC client, task submission, response parsing |
| `mcp_tools.py` | MCP tool definitions |

## Source Documentation

| Document | Path |
|:---|:---|
| README | [pi/README.md](../../../src/codomyrmex/agents/pi/README.md) |
| SPEC | [pi/SPEC.md](../../../src/codomyrmex/agents/pi/SPEC.md) |
| API Spec | [pi/API_SPECIFICATION.md](../../../src/codomyrmex/agents/pi/API_SPECIFICATION.md) |
| MCP Tools | [pi/MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/agents/pi/MCP_TOOL_SPECIFICATION.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/pi/](../../../src/codomyrmex/agents/pi/)
- **Project Root**: [README.md](../../../README.md)
