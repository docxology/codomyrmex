# AI Agents — Functional Specification

**Module**: `codomyrmex.agents`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Agents Module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|

### Submodule Structure

- `ai_code_editing/` — AI Code Editing Module for Codomyrmex.
- `claude/` — Claude API integration for Codomyrmex agents.
- `cli/` — CLI agent implementation.
- `codex/` — OpenAI Codex integration for Codomyrmex agents.
- `core/` — Core agent infrastructure and base classes.
- `deepseek/` — Deepseek Submodule
- `droid/` — Droid configuration and operation package.
- `evaluation/` — Agent Evaluation Module
- `every_code/` — Every Code CLI integration for Codomyrmex agents.
- `gemini/` — Gemini Agent Integration.
- `generic/` — Generic agent utilities and base classes.
- `git_agent/` — Git operations agent.
- `history/` — Agent History Module
- `infrastructure/` — Infrastructure agent for cloud operations.
- `jules/` — Jules CLI integration for Codomyrmex agents.
- `mistral_vibe/` — Mistral Vibe CLI integration for Codomyrmex agents.
- `o1/` — O1 Submodule
- `opencode/` — OpenCode CLI integration for Codomyrmex agents.
- `pooling/` — Agent Pooling Module
- `qwen/` — Qwen Submodule
- `theory/` — Theoretical foundations for agentic systems.

### Source Files

- `exceptions.py`

## 3. Dependencies

See `src/codomyrmex/agents/__init__.py` for import dependencies.

## 4. Public API

See source module for available exports.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k agents -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/agents/)
