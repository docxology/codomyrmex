# Agents Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

AI agent framework providing integrations with multiple AI providers and code editing capabilities. Supports Claude, Codex, Gemini, Jules, and Mistral backends.

## Key Features

- **Multi-Provider Support**: Claude, Codex, Gemini, Jules, Mistral
- **AI Code Editing**: Intelligent code generation and refactoring
- **Task Management**: Droid-based task orchestration
- **Agent Orchestration**: Coordinate multiple agents

## Key Components

| Component | Description |
|-----------|-------------|
| `ai_code_editing/` | AI-powered code generation |
| `claude/` | Anthropic Claude integration |
| `codex/` | OpenAI Codex integration |
| `gemini/` | Google Gemini integration |
| `jules/` | Jules agent integration |
| `droid/` | Task management framework |

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

## Related Modules

- [llm](../llm/) - LLM provider abstraction
- [model_context_protocol](../model_context_protocol/) - MCP interface
- [cerebrum](../cerebrum/) - Reasoning engine

## Navigation

- **Source**: [src/codomyrmex/agents/](../../../src/codomyrmex/agents/)
- **Parent**: [docs/modules/](../README.md)
