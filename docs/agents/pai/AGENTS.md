<!-- agents: curated -->

# Codomyrmex Agents — docs/agents/pai

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Path**: `docs/agents/pai`
- **Human overview**: [README.md](README.md)
- **Agent coordination** (repo root): [../../../AGENTS.md](../../../AGENTS.md)

## Purpose

Doc mirror for the **PAI agent package** (`src/codomyrmex/agents/pai/`): MCP tools, PM server, and agent wiring. Product-facing guides live under [docs/pai/](../../pai/); this folder is for agent-specific documentation that ships beside the provider tree.

## Key Files

- [README.md](README.md) — entry for this doc slice
- Code: [src/codomyrmex/agents/pai/](../../../src/codomyrmex/agents/pai/)
- Product docs: [docs/pai/](../../pai/)

## Operating Contracts

- Tool names and routes documented here must match `mcp_tools.py` and FastAPI routes under `agents/pai/pm/` (or current layout).
- Prefer linking to [docs/reference/inventory.md](../../reference/inventory.md) for aggregate MCP counts instead of hard-coding.

## Dependencies

- `uv` / `pyproject.toml` extras for PAI; runtime keys and services per [docs/pai/on-ramp.md](../../pai/on-ramp.md).

## Development Guidelines

- Follow the root [AGENTS.md](../../../AGENTS.md). Regenerate or hand-edit package docs per [docs/development/documentation.md](../../development/documentation.md).

## Navigation Links

- **Parent directory**: [agents](../README.md)
- **Project root**: ../../../README.md
