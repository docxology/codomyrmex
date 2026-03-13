# Qwen (Alibaba)

**Module**: `codomyrmex.agents.qwen` | **Category**: API-based | **Last Updated**: March 2026

## Overview

Qwen model integration via DashScope API. Supports Qwen-Coder models, native qwen-agent framework, tool/function calling, and multi-agent orchestration.

## Purpose

Comprehensive Qwen model integration providing DashScope API access, native qwen-agent framework support, tool/function calling, MCP tool exposure, and multi-agent orchestration for the Codomyrmex ecosystem.

## Source Module Structure

Source: [`src/codomyrmex/agents/qwen/`](../../../../src/codomyrmex/agents/qwen/)

### Key Files

| File | Purpose |
|:---|:---|
| [mcp_tools.py](../../../../src/codomyrmex/agents/qwen/mcp_tools.py) |  ⭐ |
| [qwen_agent_wrapper.py](../../../../src/codomyrmex/agents/qwen/qwen_agent_wrapper.py) |  ⭐ |
| [qwen_client.py](../../../../src/codomyrmex/agents/qwen/qwen_client.py) |  ⭐ |

## Configuration

**Required API Key**: `DASHSCOPE_API_KEY`

```bash
# Add to your .env or environment
DASHSCOPE_API_KEY=your-key-here
```

## Quick Start

```python
from codomyrmex.agents.qwen import QwenClient

client = QwenClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [qwen/README.md](../../../../src/codomyrmex/agents/qwen/README.md) |
| SPEC | [qwen/SPEC.md](../../../../src/codomyrmex/agents/qwen/SPEC.md) |
| AGENTS | [qwen/AGENTS.md](../../../../src/codomyrmex/agents/qwen/AGENTS.md) |
| PAI | [qwen/PAI.md](../../../../src/codomyrmex/agents/qwen/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/qwen/](../../../../src/codomyrmex/agents/qwen/)
- **Project Root**: [README.md](../../../README.md)
