# Hermes Agents

**Path**: `src/codomyrmex/agents/hermes`

## Submodule Overview

- `__init__.py`: Exports `HermesClient`, `HermesError`.
- `hermes_client.py`: Core client `HermesClient` interacting with `# hermes`.
- `mcp_tools.py`: Exposes `hermes_execute`, `hermes_skills_list`, and `hermes_status` to Claude contexts.

## Architecture

Follows `CLIAgentBase`.
Config values fallback to environment and explicitly provided configurations like `hermes_timeout` or `hermes_command`.
