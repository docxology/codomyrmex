# aider -- Technical Specification (Docs Summary)

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Subprocess-based wrapper around the `aider` CLI for AI pair programming with git-native change tracking.

## Core Interface

### AiderRunner

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(model: str = "", timeout: int = 300)` | Construct runner |
| `run_message` | `(files, instruction) -> dict` | Code mode edit |
| `run_ask` | `(files, question) -> dict` | Ask mode (no changes) |
| `run_architect` | `(files, task, editor_model) -> dict` | Architect mode |

### AiderConfig

| Field | Type | Env Var | Default |
|-------|------|---------|---------|
| `model` | `str` | `AIDER_MODEL` | `claude-sonnet-4-6` |
| `anthropic_api_key` | `str` | `ANTHROPIC_API_KEY` | `""` |
| `openai_api_key` | `str` | `OPENAI_API_KEY` | `""` |
| `timeout` | `int` | `AIDER_TIMEOUT` | `300` |

## Exception Hierarchy

```
AiderError
  +-- AiderNotInstalledError
  +-- AiderTimeoutError
  +-- AiderAPIKeyError
```

## Subprocess Contract

All calls apply: `--yes --no-pretty --no-auto-commits`

## Dependencies

- `aider-chat` >= 0.77.0 (optional: `uv tool install aider-chat`)
- Python >= 3.10

## Full Documentation

- **Detailed SPEC.md**: [src/codomyrmex/aider/SPEC.md](../../../src/codomyrmex/aider/SPEC.md)
- **API Specification**: [src/codomyrmex/aider/API_SPECIFICATION.md](../../../src/codomyrmex/aider/API_SPECIFICATION.md)
- **MCP Tools**: [src/codomyrmex/aider/MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/aider/MCP_TOOL_SPECIFICATION.md)
