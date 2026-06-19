# Agents/Codex - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview

The `agents/codex` submodule provides OpenAI Codex API integration for
Codomyrmex agents plus read-only access probes for Codex-visible Codomyrmex
capabilities. It does not mutate local Codex configuration.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `CodexClient` | Client for interacting with OpenAI Codex-compatible API calls |
| `CodexIntegrationAdapter` | Adapter bridging Codex into the Codomyrmex agent framework |

### 2.2 Functions

| Function | Description |
|----------|-------------|
| `get_codex_access_status()` | Read-only status for MCP, skill, trust, Hermes, Codex, and dispatch surfaces |
| `get_codex_dispatch_catalog()` | Read-only catalog of multiagent dispatch paths and safety classifications |

## 3. Usage Example

```python
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.codex import CodexClient, get_codex_access_status

client = CodexClient()
response = client.execute(AgentRequest(prompt="Review this parser."))
print(response.content)

status = get_codex_access_status()
print(status["surface_statuses"])
```

## 4. MCP Tools

- `codomyrmex.codex_execute`
- `codomyrmex.codex_access_status`
- `codomyrmex.codex_dispatch_catalog`

## 5. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
