# OpenCode

**Module**: `codomyrmex.agents.opencode` | **Category**: CLI-based | **Last Updated**: March 2026

## Overview

Open-source AI coding CLI built with a client/server architecture. Features context-aware code scanning, plugin-based actions/skills system, multi-file refactoring, Plan/Build mode switching, and multi-provider model support (OpenAI, Anthropic, Ollama). 26k+ GitHub stars.

**Upstream**: [opencode](https://github.com/opencode-ai/opencode)

## Key Classes

| Class | Purpose |
|:---|:---|
| `OpenCodeClient` | CLI wrapper for the `opencode` command |
| `OpenCodeIntegrationAdapter` | Cross-module integration bridge |

## Installation

```bash
npm install -g opencode
```

## CLI Commands

| Command | Purpose |
|:---|:---|
| `opencode` | Launch interactive session |
| `/init` | Analyze repo, generate agents.md |
| `/plan` | Create implementation plan (iterate with feedback) |
| `/build` | Switch to build mode — execute planned changes |
| `model` | Switch LLM provider/model |

## Configuration

Supports OpenAI, Anthropic, Ollama providers. Configure via `/init` flow.

## Usage

```python
from codomyrmex.agents.opencode import OpenCodeClient

client = OpenCodeClient()
```

## Source Module

Source: [`src/codomyrmex/agents/opencode/`](../../../src/codomyrmex/agents/opencode/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/opencode/](../../../src/codomyrmex/agents/opencode/)
- **Project Root**: [README.md](../../../README.md)
