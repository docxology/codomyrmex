# Hermes Agents

**Path**: `src/codomyrmex/agents/hermes`

## Submodule Overview

- `__init__.py`: Exports `HermesClient`, `HermesError`.
- `hermes_client.py`: Dual-backend client (CLI + Ollama) extending `CLIAgentBase`.
- `mcp_tools.py`: MCP tools: `hermes_execute`, `hermes_skills_list`, `hermes_status`.

## Architecture

Follows `CLIAgentBase`. Auto-detects backend:

1. **CLI** (`hermes` binary) — preferred if installed
2. **Ollama** (`ollama run hermes3`) — automatic fallback

## Configuration

| Key | Default | Description |
| --- | --- | --- |
| `hermes_backend` | `auto` | `auto` / `cli` / `ollama` |
| `hermes_model` | `hermes3` | Ollama model name |
| `hermes_command` | `hermes` | Path to CLI binary |
| `hermes_timeout` | `120` | Subprocess timeout (s) |

## Agent Interaction Rules

- All MCP tools lazy-import `HermesClient` to avoid circular deps.
- `hermes_execute` accepts `backend` and `model` overrides.
- Skills management (`hermes_skills_list`) requires the CLI backend.
