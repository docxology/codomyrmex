# AI Code Editing

**Module**: `codomyrmex.agents.ai_code_editing` | **Category**: Core Infrastructure | **Last Updated**: March 2026

## Overview

Diff-based code editing infrastructure. Provides structured code transforms, unified diff generation, and AI-guided file modifications across all agent backends.

## Key Classes

| Class | Purpose |
|:---|:---|
| `CodeEditor` | Structured code editing with diff tracking |
| `DiffGenerator` | Unified diff generation |
| `EditOperation` | Typed edit operation dataclass |

## Usage

```python
from codomyrmex.agents.ai_code_editing import CodeEditor

client = CodeEditor()
```

## Source Module

Source: [`src/codomyrmex/agents/ai_code_editing/`](../../../src/codomyrmex/agents/ai_code_editing/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/ai_code_editing/](../../../src/codomyrmex/agents/ai_code_editing/)
- **Project Root**: [README.md](../../../README.md)
