# Agents Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

AI agent framework providing integrations with multiple AI providers and code editing capabilities. Supports Claude, Codex, Gemini, Jules, and Mistral backends.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **Multi-Provider Support**: Claude, Codex, Gemini, Jules, Mistral
- **AI Code Editing**: Intelligent code generation and refactoring
- **Task Management**: Droid-based task orchestration
- **Agent Orchestration**: Coordinate multiple agents


### PAI Integration

When used with the [PAI system](../../../PAI.md) (`~/.claude/skills/PAI/`), the agents module serves as the primary execution layer. PAI's Algorithm selects capabilities in its THINK phase, then dispatches to codomyrmex agents during BUILD/EXECUTE. The three-tier mapping (Task Subagents → `AgentOrchestrator`, Named Agents → MCP tools, Custom Agents → `BaseAgent`) is documented in [`src/codomyrmex/agents/PAI.md`](../../../src/codomyrmex/agents/PAI.md).

## Key Components

| Component | Description |
|-----------|-------------|
| `agents/` | AI-powered code generation |
| `claude/` | Anthropic Claude integration |
| `codex/` | OpenAI Codex integration |
| `gemini/` | Google Gemini integration |
| `jules/` | Jules agent integration |
| `droid/` | Task management framework |
| `PAI.md` | PAI system bridge — agent tier mapping, capability selection, composition patterns |

## Quick Start

```python
from codomyrmex.agents import AgentOrchestrator

orchestrator = AgentOrchestrator()
result = orchestrator.execute_task("Generate a REST API handler", provider="claude")
```

## Directory Contents

- [index.md](index.md) - Module index
- [technical_overview.md](technical_overview.md) - Architecture details
- [tutorials/](tutorials/) - Usage tutorials


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k agents -v
```

## Related Modules

- [llm](../llm/) - LLM provider abstraction
- [model_context_protocol](../model_context_protocol/) - MCP interface
- [cerebrum](../cerebrum/) - Reasoning engine

## Navigation

- **Source**: [src/codomyrmex/agents/](../../../src/codomyrmex/agents/)
- **Parent**: [docs/modules/](../README.md)
