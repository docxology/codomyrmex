# AI Code Editing

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

**Module**: `codomyrmex.agents.ai_code_editing` | **Category**: Core Infrastructure | **Last Updated**: March 2026

## Overview

LLM-backed code editing helpers. Provides code generation, refactoring, quality analysis, version comparison, and documentation generation across the supported LLM providers, plus the `CodeEditor` agent that wraps them.

## Key Classes

| Class | Purpose |
| :--- | :--- |
| `CodeEditor` | `BaseAgent` wrapper that routes prompts to code generation or refactoring (`code_editor.py`) |
| `generate_code_snippet` | LLM code generation; returns a dict with `generated_code` and metadata |
| `refactor_code_snippet` | LLM refactoring of existing code; returns a dict with `refactored_code` |
| `compare_code_versions` | LLM comparison of two versions of the same code |

## Usage

```python
from codomyrmex.agents.ai_code_editing import generate_code_snippet
from codomyrmex.agents.ai_code_editing.code_editor import CodeEditor
from codomyrmex.agents.core import AgentRequest

result = generate_code_snippet("parse an ISO-8601 date string", language="python")
print(result["generated_code"])

editor = CodeEditor()
response = editor.execute(
    AgentRequest(prompt="refactor for readability", context={"code": "x=1;y=2"})
)
print(response.content)
```

## Source Module

Source: [`src/codomyrmex/agents/ai_code_editing/`](../../../src/codomyrmex/agents/ai_code_editing/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/ai_code_editing/](../../../src/codomyrmex/agents/ai_code_editing/)
- **Project Root**: [README.md](../../../README.md)

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
- **Spec**: `SPEC.md` is inherited from the nearest parent scope.
