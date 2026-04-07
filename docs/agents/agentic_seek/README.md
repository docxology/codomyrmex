# agenticSeek

**Module**: `codomyrmex.agents.agentic_seek` | **Category**: CLI-based | **Last Updated**: March 2026

## Overview

Fully-local, privacy-first autonomous agent system with multi-agent routing, web browsing, multi-language code execution, and task planning. Runs entirely on local hardware with no cloud dependency.

**Upstream**: [agenticSeek](https://github.com/Fosowl/agenticSeek)

## Key Classes

| Class | Purpose |
|:---|:---|
| `AgenticSeekClient` | Main CLI-based agent client |
| `AgenticSeekConfig` | Typed config.ini representation |
| `AgenticSeekAgentType` | Agent specialization enum |
| `AgenticSeekRouter` | Heuristic query-to-agent classifier |
| `AgenticSeekTaskPlanner` | JSON plan parsing and ordering |
| `AgenticSeekCodeExecutor` | Code block extraction and command building |
| `AgenticSeekBrowserConfig` | Browser automation settings |

## Installation

```bash
git clone https://github.com/Fosowl/agenticSeek && cd agenticSeek && pip install -e .
```

## Configuration

Configured via `config.ini`. Fully local — no API keys needed.

## Usage

```python
from codomyrmex.agents.agentic_seek import AgenticSeekClient

client = AgenticSeekClient()
```

## Source Module

Source: [`src/codomyrmex/agents/agentic_seek/`](../../../src/codomyrmex/agents/agentic_seek/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/agentic_seek/](../../../src/codomyrmex/agents/agentic_seek/)
- **Project Root**: [README.md](../../../README.md)
