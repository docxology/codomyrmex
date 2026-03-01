# PAI — Personal AI Infrastructure Scripts

**Status**: Active  
**Last Updated**: March 2026

## AI Capabilities

Orchestration scripts for the PAI dashboard ecosystem. Agents use these thin wrappers to launch, update, and validate the dual-server PAI infrastructure (`:8888` PAI Project Manager, `:8787` Codomyrmex Admin).

## Algorithm Phase Mapping

| Phase | Scripts |
|-------|---------|
| **Launch** | `dashboard.py` — start both servers, optionally open browser |
| **Generate** | `generate_skills.py` — auto-generate SKILL.md files from MCP tool manifest |
| **Update** | `update_pai_docs.py` — batch update stub PAI.md files across modules |
| **Sync** | `update_pai_skill.py` — regenerate the Codomyrmex SKILL.md tool table |
| **Validate** | `validate_pai_integration.py` — verify PAI integration health |
| **Email Test** | `test_email_compose.py` — validate LLM email compose with real project/calendar data |

## Quick Start

```bash
uv run python scripts/pai/dashboard.py           # full launch (both :8888 + :8787)
uv run python scripts/pai/dashboard.py --restart  # kill + restart both servers
uv run python scripts/pai/generate_skills.py      # regenerate all SKILL.md files
uv run python scripts/pai/validate_pai_integration.py  # check integration health
uv run python scripts/pai/test_email_compose.py --dry-run  # check email API connectivity
uv run python scripts/pai/test_email_compose.py   # full LLM email compose tests (requires ollama)
```

## Dependencies

- `codomyrmex.website` — server and data provider
- `codomyrmex.agents.pai` — trust gateway, MCP bridge
- `codomyrmex.documentation.pai` — PAI doc generation
- `codomyrmex.calendar_integration` — Google Calendar MCP tools
- `codomyrmex.email` — Gmail + AgentMail providers
- `bun` (optional) — required for PMServer.ts on `:8888`

## MCP Tools Reference

| Tool | Module | Description |
|------|--------|-------------|
| `calendar_list_events` | `calendar_integration` | List upcoming Google Calendar events |
| `calendar_create_event` | `calendar_integration` | Create a new calendar event |
| `calendar_get_event` | `calendar_integration` | Fetch event by ID |
| `calendar_update_event` | `calendar_integration` | Update event (PUT semantics) |
| `calendar_delete_event` | `calendar_integration` | Delete an event |
| `email_send_message` | `email` (AgentMail) | Send email via AgentMail |
| `email_list_messages` | `email` (AgentMail) | List inbox messages |
| `gmail_send_message` | `email` (Gmail) | Send email via Gmail |
| `gmail_list_messages` | `email` (Gmail) | List Gmail messages |

## Verification

```bash
# Run all PAI-ecosystem unit tests (445+ tests)
uv run python -m pytest src/codomyrmex/tests/unit/website/ \
  src/codomyrmex/tests/unit/agents/test_pai_bridge.py \
  src/codomyrmex/tests/unit/agents/pai/ \
  src/codomyrmex/tests/unit/email/ \
  src/codomyrmex/tests/unit/calendar_integration/ -v
```

## Error Handling

All PAI functions use defensive error isolation:

- **File I/O**: YAML/JSON parsing wrapped in `try`/`except` with `logger.debug`
- **Path traversal**: `get_pai_tasks()` rejects `..` and `/` in project IDs
- **Mermaid graph**: `_safe_mermaid_graph()` returns fallback on any exception
- **Awareness data**: Each data source isolated — failures in one don't block others
