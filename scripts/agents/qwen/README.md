# Qwen Agent Scripts

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Thin orchestrator scripts demonstrating the `codomyrmex.agents.qwen` module. These scripts delegate all business logic to the source module at `src/codomyrmex/agents/qwen/`.

## Scripts

| Script | Description |
|--------|-------------|
| `qwen_demo.py` | Comprehensive demo — 8 capabilities (registry, MCP, wrapper, chat, streaming, tools, code review) |

## Quick Start

```bash
# Offline demo (no API key needed)
uv run scripts/agents/qwen/qwen_demo.py --offline

# Full demo (requires DASHSCOPE_API_KEY)
export DASHSCOPE_API_KEY="your-key"
uv run scripts/agents/qwen/qwen_demo.py

# Custom model
uv run scripts/agents/qwen/qwen_demo.py --model qwen3-max
```

## Demo Capabilities

1. **Model Registry** — 14 models, categories, code models
2. **MCP Tools** — 5 tools verified offline
3. **Wrapper Functions** — qwen-agent framework availability
4. **Client Construction** — capabilities, base_url
5. **Chat** — Single-turn code generation
6. **Streaming** — Real-time token streaming
7. **Tool Calling** — Multi-turn function calling loop
8. **Code Review** — Via `qwen_code_review` MCP tool

## Source Module

All logic lives in [`src/codomyrmex/agents/qwen/`](../../../src/codomyrmex/agents/qwen/):

- `qwen_client.py` — DashScope API client (14 models, tool calling)
- `qwen_agent_wrapper.py` — Native qwen-agent framework
- `mcp_tools.py` — 5 MCP tool definitions

## Navigation

- **Parent**: [scripts/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/qwen/](../../../src/codomyrmex/agents/qwen/)
