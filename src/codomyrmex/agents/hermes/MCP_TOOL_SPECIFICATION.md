# Hermes — MCP tools

**Module**: `codomyrmex.agents.hermes`  
**Definitions**: [`mcp_tools.py`](mcp_tools.py)

## Summary

- Tools are registered with `@mcp_tool(category="hermes", …)` from `codomyrmex.model_context_protocol.decorators`.
- Skill-interop entrypoints use `tags=["hermes", "skills", "cli_preload", "interop"]` so PAI `get_skill_manifest()` and MCP discovery can filter by tag.
- Optional arguments **`hermes_skill`** / **`hermes_skills`** on execute/stream/chat/batch/sampling forward to `HermesClient` and become `hermes chat -s` on the CLI backend only.
- **`hermes_skills_resolve`** / **`hermes_skills_validate_registry`** implement the unified registry workflow (`skill_registry.py`, bundled `data/skills_registry.yaml`, optional `CODOMYRMEX_SKILLS_REGISTRY`, project `.codomyrmex/hermes_skills_profile.yaml`).
- **`hermes_fastmcp_scaffold`** wraps `optional-skills/mcp/fastmcp/scaffold_fastmcp.py` to generate FastMCP server boilerplate for Codomyrmex↔Hermes MCP exposure.

## Discovery

- Runtime scan: package `codomyrmex.agents.hermes` → `mcp_tools` submodule.
- Manifest: `codomyrmex.agents.pai.mcp.server.get_skill_manifest()` includes `tags` per tool.

## Related docs

- [docs/agents/hermes/skills.md](../../../../../docs/agents/hermes/skills.md)
- [docs/agents/hermes/tools.md](../../../../../docs/agents/hermes/tools.md)
