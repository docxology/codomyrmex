# Mistral Vibe

**Module**: `codomyrmex.agents.mistral_vibe` | **Category**: CLI-based | **Last Updated**: March 2026

## Overview

Mistral AI integration via the vibe CLI tool (`vibe`, `vibe-acp`). Supports Mistral models with API key authentication and streaming.

## Purpose

The `mistral_vibe` submodule provides integration with Mistral Vibe CLI tool. It includes a client wrapper for executing vibe commands and integration adapters for Codomyrmex modules.

## Source Module Structure

Source: [`src/codomyrmex/agents/mistral_vibe/`](../../../../src/codomyrmex/agents/mistral_vibe/)

### Key Files

| File | Purpose |
|:---|:---|
| [mcp_tools.py](../../../../src/codomyrmex/agents/mistral_vibe/mcp_tools.py) |  ⭐ |
| [mistral_vibe_client.py](../../../../src/codomyrmex/agents/mistral_vibe/mistral_vibe_client.py) |  ⭐ |
| [mistral_vibe_integration.py](../../../../src/codomyrmex/agents/mistral_vibe/mistral_vibe_integration.py) |  |

## Configuration

**Required API Key**: `MISTRAL_API_KEY`

```bash
# Add to your .env or environment
MISTRAL_API_KEY=your-key-here
```

## Quick Start

```python
from codomyrmex.agents.mistral_vibe import MistralVibeClient

client = MistralVibeClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [mistral_vibe/README.md](../../../../src/codomyrmex/agents/mistral_vibe/README.md) |
| SPEC | [mistral_vibe/SPEC.md](../../../../src/codomyrmex/agents/mistral_vibe/SPEC.md) |
| AGENTS | [mistral_vibe/AGENTS.md](../../../../src/codomyrmex/agents/mistral_vibe/AGENTS.md) |
| PAI | [mistral_vibe/PAI.md](../../../../src/codomyrmex/agents/mistral_vibe/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/mistral_vibe/](../../../../src/codomyrmex/agents/mistral_vibe/)
- **Project Root**: [README.md](../../../README.md)
