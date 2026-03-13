# Every Code

**Module**: `codomyrmex.agents.every_code` | **Category**: CLI-based | **Last Updated**: March 2026

## Overview

Multi-agent orchestration via the Every Code CLI. Supports /plan (multi-agent consensus), /solve (fastest agent), /code (multi-agent with worktrees), /auto (auto-drive), and /browser integration.

## Purpose

The `every_code` submodule provides integration with Every Code CLI tool. Every Code is a fork of the Codex CLI that includes validation, automation, browser integration, multi-agents, theming, and enhanced reasoning controls. It can orchestrate agents from OpenAI, Claude, Gemini, or any provider.

## Source Module Structure

Source: [`src/codomyrmex/agents/every_code/`](../../../../src/codomyrmex/agents/every_code/)

### Key Files

| File | Purpose |
|:---|:---|
| [every_code_client.py](../../../../src/codomyrmex/agents/every_code/every_code_client.py) |  ⭐ |
| [every_code_integration.py](../../../../src/codomyrmex/agents/every_code/every_code_integration.py) |  |
| [mcp_tools.py](../../../../src/codomyrmex/agents/every_code/mcp_tools.py) |  ⭐ |

## Quick Start

```python
from codomyrmex.agents.every_code import EveryCodeClient

client = EveryCodeClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [every_code/README.md](../../../../src/codomyrmex/agents/every_code/README.md) |
| SPEC | [every_code/SPEC.md](../../../../src/codomyrmex/agents/every_code/SPEC.md) |
| AGENTS | [every_code/AGENTS.md](../../../../src/codomyrmex/agents/every_code/AGENTS.md) |
| PAI | [every_code/PAI.md](../../../../src/codomyrmex/agents/every_code/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/every_code/](../../../../src/codomyrmex/agents/every_code/)
- **Project Root**: [README.md](../../../README.md)
