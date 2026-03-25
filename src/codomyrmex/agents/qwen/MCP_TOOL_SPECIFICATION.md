# qwen — MCP Tool Specification

## Overview

Qwen / DashScope and Qwen-Agent helpers. Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Tags vary per tool.

## Tools

| Tool | Summary |
|:-----|:--------|
| `qwen_chat` | Chat completion with optional system prompt |
| `qwen_chat_with_tools` | Tool-calling loop (OpenAI-format tools) |
| `qwen_list_models` | Registry of Qwen models |
| `qwen_create_agent` | Build Qwen-Agent `Assistant` |
| `qwen_code_review` | Code review via Qwen-Coder |

### `qwen_chat`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `message` | string | — | User message (required) |
| `model` | string | `qwen-coder-turbo` | Model id |
| `system_prompt` | string | `""` | System message |
| `temperature` | float | `0.7` | Sampling temperature |
| `max_tokens` | integer | `4096` | Max output tokens |

### `qwen_chat_with_tools`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `messages` | array | — | Conversation |
| `tools` | array | — | OpenAI-format tool defs |
| `model` | string | `qwen3-max` | Model id |
| `max_iterations` | integer | `5` | Tool rounds |

### `qwen_create_agent`

Keyword-only: `model`, `tools`, `system_message` (see [`mcp_tools.py`](mcp_tools.py)).

### `qwen_code_review`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `code` | string | — | Source to review |
| `language` | string | `python` | Language |
| `focus` | string | `general` | `general`, `security`, `performance`, `style` |
| `model` | string | `qwen-coder-turbo` | Model id |

## Navigation

- **Parent**: [agents](../README.md)
- **Project root**: [README.md](../../../../README.md)
