# Claude (Anthropic)

**Module**: `codomyrmex.agents.claude` | **Category**: API-based | **Last Updated**: March 2026

## Overview

Anthropic Claude integration for high-quality code generation, complex reasoning, and production use. Supports Claude 3 Opus/Sonnet/Haiku models with streaming and multi-turn conversations.

## Purpose

The `claude` submodule provides comprehensive integration with Anthropic's Claude API for AI-assisted coding. Includes full-featured API client, integration adapters, and Claude Code capabilities for agentic coding workflows.

## Source Module Structure

Source: [`src/codomyrmex/agents/claude/`](../../../../src/codomyrmex/agents/claude/)

### Key Files

| File | Purpose |
|:---|:---|
| [claude_client.py](../../../../src/codomyrmex/agents/claude/claude_client.py) |  ⭐ |
| [claude_integration.py](../../../../src/codomyrmex/agents/claude/claude_integration.py) |  |
| [mcp_tools.py](../../../../src/codomyrmex/agents/claude/mcp_tools.py) |  ⭐ |

### Subdirectories

- `mixins/`

## Configuration

**Required API Key**: `ANTHROPIC_API_KEY`

```bash
# Add to your .env or environment
ANTHROPIC_API_KEY=your-key-here
```

## Quick Start

```python
from codomyrmex.agents.claude import ClaudeClient

client = ClaudeClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [claude/README.md](../../../../src/codomyrmex/agents/claude/README.md) |
| SPEC | [claude/SPEC.md](../../../../src/codomyrmex/agents/claude/SPEC.md) |
| AGENTS | [claude/AGENTS.md](../../../../src/codomyrmex/agents/claude/AGENTS.md) |
| PAI | [claude/PAI.md](../../../../src/codomyrmex/agents/claude/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/claude/](../../../../src/codomyrmex/agents/claude/)
- **Project Root**: [README.md](../../../README.md)
