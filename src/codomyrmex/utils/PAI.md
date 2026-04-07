# Personal AI Infrastructure — Utils Module

**Version**: v1.2.8 | **Status**: Active | **Last Updated**: April 2026

## Overview

Shared utilities across Codomyrmex: safe JSON, file hashing, subprocess execution, script scaffolding, timing, and **retry** helpers. Uses `codomyrmex.logging_monitoring` for structured logs.

## PAI capabilities

- Path and directory helpers (`ensure_directory`)
- JSON parse/serialize with safe fallbacks
- Content and file hashing (algorithm parameter, e.g. `sha256`)
- Subprocess execution and optional streaming (`process/`)
- **Retry**: simple package `retry` vs configurable `retry_sync` / `async_retry` (see [API_SPECIFICATION.md](API_SPECIFICATION.md))

## Key exports (selected)

| Export | Notes |
|--------|--------|
| `retry` | From `codomyrmex.utils` — sync, exponential delay via `delay` × `backoff`. |
| `RetryConfig`, `async_retry` | From package `__all__`; defined in `retry_sync.py`. |
| `run_command`, `run_command_async` | Subprocess with structured results. |
| `ScriptBase`, `ScriptConfig` | Executable script contract. |

Full list: `codomyrmex.utils.__all__` (see [SPEC.md](SPEC.md)).

## PAI algorithm phase mapping

| Phase | Utils contribution |
|-------|---------------------|
| **All** | Cross-cutting helpers and stable primitives |

## Architecture role

**Foundation** — low-level helpers consumed widely. Keep imports shallow and avoid circular ties to higher layers.

## MCP tools

Exposed via `mcp_tools.py` for agent surfaces; see [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md).

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md)
- **Root bridge**: [../../../PAI.md](../../../PAI.md)
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
