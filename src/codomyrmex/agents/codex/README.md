# codex

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: June 2026

## Overview

The `codex` module contains the OpenAI Codex API client, Codomyrmex integration
adapter, and read-only access probes that let Codex enumerate Codomyrmex MCP
tools, skill packs, trust state, Hermes skill visibility, and multiagent
dispatch surfaces.

## Key Files

- `access.py` - Read-only Codex access status and dispatch catalog helpers.
- `codex_client.py` - `AgentInterface` implementation backed by the OpenAI API.
- `codex_integration.py` - Adapter for Codomyrmex code editing, LLM, and analysis flows.
- `mcp_tools.py` - MCP tools: `codex_execute`, `codex_access_status`, and `codex_dispatch_catalog`.

## Safe Inspection

```bash
uv run python scripts/agents/codex_access.py --json
uv run python scripts/agents/improve_src.py --dry-run --limit 2 --json
```

These commands do not call remote model APIs, mutate trust state, or launch
agents. Real dispatch remains opt-in through the dispatch surfaces listed in the
catalog.

## Navigation

- **Parent Directory**: [agents](../README.md)
- **Project Root**: ../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
- **MCP tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
