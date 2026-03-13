# Agents/Codex - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `agents/codex` submodule provides OpenAI Codex integration for Codomyrmex agents. Wraps the Codex CLI and API for agentic code editing tasks.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `CodexClient` | Client for interacting with OpenAI Codex (CLI wrapper + API) |
| `CodexIntegrationAdapter` | Adapter bridging Codex into the Codomyrmex agent framework |

## 3. Usage Example

```python
from codomyrmex.agents.codex import CodexClient

client = CodexClient()
response = client.complete("Fix the bug in this function", context="def add(a, b): return a - b")
print(response.code)
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
