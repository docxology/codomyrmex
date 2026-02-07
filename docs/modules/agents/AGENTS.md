# AI Agents Module — Agent Coordination

## Purpose

Agents Module for Codomyrmex.

## Key Capabilities

- AI Agents operations and management

## Agent Usage Patterns

```python
from codomyrmex.agents import *

# Agent uses ai agents capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/agents/](../../../src/codomyrmex/agents/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components


### Submodules

- `ai_code_editing` — Ai Code Editing
- `claude` — Claude
- `cli` — CLI
- `codex` — Codex
- `core` — Core
- `deepseek` — Deepseek
- `droid` — Droid
- `evaluation` — Evaluation

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k agents -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
