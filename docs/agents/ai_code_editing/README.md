# AI Code Editing

**Module**: `codomyrmex.agents.ai_code_editing` | **Category**: Core Infrastructure | **Last Updated**: March 2026

## Overview

Core code editing abstractions used by all agents. Provides diff-based editing, code transformation pipelines, and structured code modification protocols.

## Purpose

The `ai_code_editing` module serves as the semantic intelligence layer of Codomyrmex. It abstracts the complexity of interacting with various LLM providers (OpenAI, Anthropic, Google, **Ollama**) to provide high-level code manipulation capabilities: generation, refactoring, analysis, and documentation.

## Source Module Structure

Source: [`src/codomyrmex/agents/ai_code_editing/`](../../../../src/codomyrmex/agents/ai_code_editing/)

### Key Files

| File | Purpose |
|:---|:---|
| [_execution.py](../../../../src/codomyrmex/agents/ai_code_editing/_execution.py) |  |
| [_planning.py](../../../../src/codomyrmex/agents/ai_code_editing/_planning.py) |  |
| [claude_task_master.py](../../../../src/codomyrmex/agents/ai_code_editing/claude_task_master.py) |  |
| [code_editor.py](../../../../src/codomyrmex/agents/ai_code_editing/code_editor.py) |  |
| [droid_manager.py](../../../../src/codomyrmex/agents/ai_code_editing/droid_manager.py) |  |
| [openai_codex.py](../../../../src/codomyrmex/agents/ai_code_editing/openai_codex.py) |  |
| [prompt_composition.py](../../../../src/codomyrmex/agents/ai_code_editing/prompt_composition.py) |  |

### Subdirectories

- `ai_code_helpers/`

## Quick Start

```python
from codomyrmex.agents.ai_code_editing import AiCodeEditingClient

client = AiCodeEditingClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [ai_code_editing/README.md](../../../../src/codomyrmex/agents/ai_code_editing/README.md) |
| SPEC | [ai_code_editing/SPEC.md](../../../../src/codomyrmex/agents/ai_code_editing/SPEC.md) |
| AGENTS | [ai_code_editing/AGENTS.md](../../../../src/codomyrmex/agents/ai_code_editing/AGENTS.md) |
| PAI | [ai_code_editing/PAI.md](../../../../src/codomyrmex/agents/ai_code_editing/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/ai_code_editing/](../../../../src/codomyrmex/agents/ai_code_editing/)
- **Project Root**: [README.md](../../../README.md)
