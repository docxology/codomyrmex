# Codex (OpenAI)

**Module**: `codomyrmex.agents.codex` | **Category**: API-based | **Last Updated**: March 2026

## Overview

OpenAI Codex CLI integration for autonomous coding tasks. Codex authenticates via device-code flow (browser OAuth), runs tasks in sandboxed environments, and supports project-wide code generation and editing.

## Key Classes

| Class | Purpose |
|:---|:---|
| `CodexClient` | CLI wrapper for the `codex` command |
| `CodexIntegrationAdapter` | Bridges Codex with other Codomyrmex modules |

## Usage

```python
from codomyrmex.agents.codex import CodexClient

client = CodexClient()
response = client.execute(AgentRequest(prompt="Add error handling to parser.py"))
```

## Configuration

**Auth**: Device-code flow — no API key needed. Credentials stored at `~/.codex/auth.json`.

```bash
codex login   # Opens browser for OAuth
```

## Source Module

Source: [`src/codomyrmex/agents/codex/`](../../../src/codomyrmex/agents/codex/)

| File | Purpose |
|:---|:---|
| `codex_client.py` | CLI wrapper, task submission, response parsing |
| `codex_integration.py` | Integration adapter |
| `mcp_tools.py` | MCP tool definitions |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/codex/](../../../src/codomyrmex/agents/codex/)
- **Project Root**: [README.md](../../../README.md)
