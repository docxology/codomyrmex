# Codex (OpenAI)

**Module**: `codomyrmex.agents.codex` | **Category**: API-based | **Last Updated**: March 2026

## Overview

OpenAI Codex integration for code-focused models. Supports code completion, editing, and analysis via the OpenAI API with streaming and temperature control.

## Purpose

The `codex` submodule provides integration with OpenAI Codex API. It includes a client for interacting with Codex API and integration adapters for Codomyrmex modules.

## Source Module Structure

Source: [`src/codomyrmex/agents/codex/`](../../../../src/codomyrmex/agents/codex/)

### Key Files

| File | Purpose |
|:---|:---|
| [codex_client.py](../../../../src/codomyrmex/agents/codex/codex_client.py) |  ⭐ |
| [codex_integration.py](../../../../src/codomyrmex/agents/codex/codex_integration.py) |  |
| [mcp_tools.py](../../../../src/codomyrmex/agents/codex/mcp_tools.py) |  ⭐ |

## Configuration

**Required API Key**: `OPENAI_API_KEY`

```bash
# Add to your .env or environment
OPENAI_API_KEY=your-key-here
```

## Quick Start

```python
from codomyrmex.agents.codex import CodexClient

client = CodexClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [codex/README.md](../../../../src/codomyrmex/agents/codex/README.md) |
| SPEC | [codex/SPEC.md](../../../../src/codomyrmex/agents/codex/SPEC.md) |
| AGENTS | [codex/AGENTS.md](../../../../src/codomyrmex/agents/codex/AGENTS.md) |
| PAI | [codex/PAI.md](../../../../src/codomyrmex/agents/codex/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/codex/](../../../../src/codomyrmex/agents/codex/)
- **Project Root**: [README.md](../../../README.md)
