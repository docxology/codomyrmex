# PAI — Personal AI Infrastructure Scripts

**Status**: Active  
**Last Updated**: February 2026

## AI Capabilities

Orchestration scripts for the PAI dashboard ecosystem. Agents use these thin wrappers to launch, update, and validate the dual-server PAI infrastructure (`:8787` Codomyrmex Admin, `:8888` PAI Project Manager).

## Algorithm Phase Mapping

| Phase | Scripts |
|-------|---------|
| **Launch** | `dashboard.py` — start both servers, optionally open browser |
| **Generate** | `generate_skills.py` — auto-generate SKILL.md files from MCP tool manifest |
| **Update** | `update_pai_docs.py` — batch update stub PAI.md files across modules |
| **Sync** | `update_pai_skill.py` — regenerate the Codomyrmex SKILL.md tool table |
| **Validate** | `validate_pai_integration.py` — verify PAI integration health |

## Quick Start

```bash
uv run python scripts/pai/dashboard.py           # full launch
uv run python scripts/pai/dashboard.py --restart  # kill + restart
uv run python scripts/pai/generate_skills.py      # regenerate all SKILL.md files
uv run python scripts/pai/validate_pai_integration.py  # check integration
```

## Dependencies

- `codomyrmex.website` — server and data provider
- `codomyrmex.agents.pai` — trust gateway, MCP bridge
- `codomyrmex.documentation.pai` — PAI doc generation
- `bun` (optional) — required for PMServer.ts on `:8888`
