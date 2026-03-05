# Qwen Agent Integration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Comprehensive Qwen model integration for the Codomyrmex ecosystem. Supports Alibaba's full Qwen model family through two complementary interfaces:

1. **`QwenClient`** — OpenAI-compatible client via DashScope API
2. **`qwen_agent_wrapper`** — Native qwen-agent framework with MCP server support

## Supported Models

| Model | Context | Category |
|-------|---------|----------|
| `qwen3-max` | 128K | Flagship reasoning |
| `qwen3-plus` | 128K | Flagship |
| `qwen3-mini` | 128K | Lightweight |
| `qwen-coder-turbo` | 128K | **Code** (default) |
| `qwen-coder-plus` | 128K | Code |
| `qwen2.5-coder-32b` | 32K | Code (self-hosted) |
| `qwen-turbo` | 128K | General |
| `qwen-max` | 128K | General |
| `qwen-long` | 1M | Long-context |
| `qwen-vl-max` | 32K | Vision |

## Quick Start

```python
# --- DashScope API (OpenAI-compatible) ---
from codomyrmex.agents.qwen import QwenClient

client = QwenClient()
response = client._execute_impl(request)

# With tool calling
result = client.chat_with_tools(
    messages=[{"role": "user", "content": "What time is it?"}],
    tools=[...],  # OpenAI-format tool defs
    tool_executor=my_executor,
)

# --- Native Qwen-Agent Framework ---
from codomyrmex.agents.qwen import create_assistant, run_assistant

assistant = create_assistant(
    model="qwen-coder-turbo",
    tools=["code_interpreter"],
    mcp_servers={"fetch": {"command": "uvx", "args": ["mcp-server-fetch"]}},
)
answer = run_assistant(assistant, "Explain this code")
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `qwen_chat` | Send chat message to any Qwen model |
| `qwen_chat_with_tools` | Multi-turn tool-calling loop |
| `qwen_list_models` | List all models with metadata |
| `qwen_create_agent` | Create qwen-agent Assistant |
| `qwen_code_review` | Code review via Qwen-Coder |

## Directory Contents

```
qwen/
├── __init__.py              # Module exports (lazy imports)
├── qwen_client.py           # OpenAI-compatible DashScope client
├── qwen_agent_wrapper.py    # Native qwen-agent framework wrapper
├── mcp_tools.py             # 5 MCP tool definitions
├── README.md                # This file
├── AGENTS.md                # Agent coordination
├── SPEC.md                  # Functional specification
├── PAI.md                   # PAI integration
└── py.typed                 # PEP 561 typing marker
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DASHSCOPE_API_KEY` | DashScope API key | — |
| `QWEN_API_KEY` | Alternative API key env | — |
| `QWEN_BASE_URL` | API base URL | `https://dashscope.aliyuncs.com/compatible-mode/v1` |

## Dependencies

- **Required**: `openai` (for DashScope compatible-mode API)
- **Optional**: `qwen-agent` (for native framework, WebUI, MCP servers)
- **Optional**: `gradio` (for WebUI)

## Navigation

- **Parent Module**: [agents/](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
