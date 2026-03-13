# Qwen (Alibaba)

**Module**: `codomyrmex.agents.qwen` | **Category**: API-based | **Version**: v1.2.2 | **Last Updated**: March 2026

## Overview

Comprehensive Qwen model integration supporting DashScope API via OpenAI-compatible client, native `qwen-agent` framework (Assistant, WebUI, MCP), 14 model variants, and tool/function calling with multi-turn loops.

## Key Classes

| Class | Purpose |
|:---|:---|
| `QwenClient` | DashScope API client (OpenAI-compatible) |
| `QWEN_MODELS` | Registry of 14 model variants |
| `DEFAULT_MODEL` | Default model identifier |

## Qwen-Agent Framework (Lazy Import)

| Function | Purpose |
|:---|:---|
| `create_assistant()` | Create a Qwen assistant |
| `create_codomyrmex_assistant()` | Project-aware assistant |
| `launch_webui()` | Launch interactive web UI |
| `run_assistant(prompt)` | Single-turn assistant execution |
| `stream_assistant(prompt)` | Streaming assistant execution |

## Model Variants

- **Qwen3-Max** — Flagship reasoning model
- **Qwen-Coder** — Code-specialized models
- **Qwen-VL** — Vision-language models
- **Qwen-Audio** — Audio understanding
- 10+ additional variants

## Usage

```python
from codomyrmex.agents.qwen import QwenClient, QWEN_MODELS

# Basic usage
client = QwenClient()
response = client.execute(AgentRequest(prompt="Explain this code"))

# With specific model
client = QwenClient(model="qwen3-max")

# Native framework (lazy import)
from codomyrmex.agents.qwen import create_codomyrmex_assistant
assistant = create_codomyrmex_assistant()
```

## Configuration

**Required API Key**: `DASHSCOPE_API_KEY`

```bash
export DASHSCOPE_API_KEY=your-key-here
```

## Source Module

Source: [`src/codomyrmex/agents/qwen/`](../../../../src/codomyrmex/agents/qwen/)

| File | Purpose |
|:---|:---|
| `qwen_client.py` | DashScope API client, model registry |
| `qwen_agent_wrapper.py` | Native qwen-agent framework wrapper |
| `mcp_tools.py` | 5 MCP tools for agent consumption |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/qwen/](../../../../src/codomyrmex/agents/qwen/)
- **Project Root**: [README.md](../../../README.md)
