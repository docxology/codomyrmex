# DeepSeek

**Module**: `codomyrmex.agents.deepseek` | **Category**: API-based | **Version**: v1.2.3 | **Last Updated**: March 2026

## Overview

DeepSeek Coder integration for code generation and analysis. Provides API access to DeepSeek's code-specialized models with OpenAI-compatible interface.

## Key Classes

| Class | Purpose |
|:---|:---|
| `DeepSeekClient` | API client for DeepSeek code models |

## Usage

```python
from codomyrmex.agents.deepseek import DeepSeekClient

client = DeepSeekClient()
response = client.execute(AgentRequest(prompt="Generate a Python parser"))
```

## Configuration

**Required API Key**: `DEEPSEEK_API_KEY`

```bash
export DEEPSEEK_API_KEY=your-key-here
```

## Source Module

Source: [`src/codomyrmex/agents/deepseek/`](../../../../src/codomyrmex/agents/deepseek/)

| File | Purpose |
|:---|:---|
| `deepseek_client.py` | OpenAI-compatible API client |
| `mcp_tools.py` | MCP tool definitions |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/deepseek/](../../../../src/codomyrmex/agents/deepseek/)
- **Project Root**: [README.md](../../../README.md)
