# Mistral Vibe

**Module**: `codomyrmex.agents.mistral_vibe` | **Category**: CLI-based | **Last Updated**: March 2026

## Overview

Mistral's open-source AI coding CLI powered by Devstral 2 models. Conversational codebase exploration, code generation/refactoring, test/lint running, and terminal-first scriptable workflows. Supports watch mode for file changes.

**Upstream**: [mistral-vibe](https://github.com/mistralai/mistral-vibe)

## Key Classes

| Class | Purpose |
|:---|:---|
| `MistralVibeClient` | CLI wrapper for the `vibe` command |
| `MistralVibeIntegrationAdapter` | Cross-module integration bridge |

## Installation

```bash
curl -LsSf https://mistral.ai/vibe/install.sh | bash
# or: pip install mistral-vibe-cli
```

## CLI Commands

| Command | Purpose |
|:---|:---|
| `vibe` | Launch interactive coding session |
| `vibe -h` | Show help and available commands |
| Slash commands | Configure model, lock files, set themes |

## Configuration

**Required**: `MISTRAL_API_KEY` from console.mistral.ai

## Usage

```python
from codomyrmex.agents.mistral_vibe import MistralVibeClient

client = MistralVibeClient()
```

## Source Module

Source: [`src/codomyrmex/agents/mistral_vibe/`](../../../src/codomyrmex/agents/mistral_vibe/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/mistral_vibe/](../../../src/codomyrmex/agents/mistral_vibe/)
- **Project Root**: [README.md](../../../README.md)
