# docs/pai — Functional Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Expanded reference documentation for the PAI-Codomyrmex integration. Supplements the root `PAI.md` bridge document with detailed architecture, API, and tool references. The PAI Dashboard (port 8889) is a Codomyrmex-integrated fork of [danielmiessler/Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure).

![PAI Analytics — Primary dashboard interface showing mission, project, and task metrics](screenshots/pai_analytics.png)

## Scope

| Document | Covers |
|----------|--------|
| `architecture.md` | Component diagram, data flow, trust model, cross-language communication |
| `tools-reference.md` | All 22 static tools with parameters, trust levels; dynamic discovery mechanism |
| `api-reference.md` | PAIBridge (24 methods), TrustRegistry, module functions, dataclasses, constants |
| `workflows.md` | `/codomyrmexVerify`, `/codomyrmexTrust`, Algorithm phase mapping |
| `screenshots/` | PAI Dashboard interface screenshots (8 tabs) |

## Capability Specifications

### Codomyrmex Admin Dashboard (port 8787)

Started with: `uv run python -m codomyrmex.website.server` or `scripts/website/launch_dashboard.py`

| Tab | Endpoint | Data Source | Live/Async |
|-----|----------|-------------|------------|
| Overview | `GET /api/status` | `DataProvider.get_system_summary()` | Static |
| Modules | `GET /api/modules` | `DataProvider.get_modules()` | Static |
| Agents | `GET /api/agents` | `DataProvider.get_actual_agents()` | Static |
| Scripts | `GET /api/scripts` + `POST /api/execute` | `scripts/` directory scan | Sync exec |
| Config | `GET/POST /api/config/*` | Config files (`.json`, `.toml`, `.yaml`) | Static |
| Docs | `GET /api/docs/*` | `docs/` directory | Static |
| Tools | `GET /api/tools` | MCP tool manifest (auto-discovered) | Static |
| Tests | `POST /api/tests` + `GET /api/tests/status` | pytest subprocess | Async poll |
| Chat | `POST /api/chat` | Ollama proxy → `POST /api/chat` | Sync |
| Health | `GET /api/health` | git, Python, architecture layers | Static |
| Telemetry | `GET /api/telemetry` | `MetricCollector` (in-process) | Persistent |
| PAI Control | `POST /api/pai/action` | PAIBridge + trust gateway | Varies |
| Awareness | `GET /api/awareness` | `~/.claude/` PAI filesystem | Static |
| Dispatch | `POST /api/agent/dispatch` | `ConversationOrchestrator` | Async poll |

### PAI Project Manager Dashboard (port 8888)

Started with: `bun run ~/.claude/PAI/Tools/PMServer.ts` (TypeScript/Bun)

| Tab | Purpose |
|-----|---------|
| Analytics | Mission/project/task KPIs, completion rates |
| Board | Kanban with ACTIVE, PLANNING, IN PROGRESS, BLOCKED, PAUSED columns |
| Calendar | Google Calendar integration, event creation |
| Email | AgentMail + Gmail dual-provider, AI-assisted drafting |
| Network | Force-directed project→task relationship graph |
| Git | Repository sync, branch management |
| Dispatch | Algorithm phase execution buttons (Summarize, Scope & Plan, Review, Enact) |
| Integration | GitHub bridge, PR/issue tracking |

### MCP Tool Counts (v1.0.8)

| Category | Count | Notes |
|----------|-------|-------|
| Static proxy tools | 22 | File ops, git, shell, analysis, PAI, testing, workflows |
| Dynamic auto-discovered | ~407 | From 121 modules with `mcp_tools.py` + `@mcp_tool` |
| Destructive (trust-gated) | 4 | `write_file`, `run_command`, `run_tests`, `call_module_function` |
| Resources | 3 | `codomyrmex://modules`, `codomyrmex://status`, discovery metrics |
| Prompts | 10 | Analysis, review, and generation prompt templates |

## Design Principles

1. **Hierarchy**: Root PAI.md (bridge overview) → docs/pai/ (detailed reference) → src/ (implementation docs)
2. **No duplication**: Each document has a unique scope — no verbatim copying from root PAI.md
3. **Synchronized**: All counts (22 tools, 10 prompts, 3 resources, 4 destructive) match implementation
4. **Visual**: Interface screenshots embedded in context alongside the features they document

## Dashboard Tabs Covered

| Tab | Screenshot | Primary Doc |
|-----|-----------|-------------|
| Analytics | `screenshots/pai_analytics.png` | `api-reference.md` — PAI status/awareness |
| Board | `screenshots/pai_board.png` | `workflows.md` — Mission lifecycle tracking |
| Calendar | `screenshots/pai_calendar.png` | `workflows.md` — Scheduling integration |
| Email | `screenshots/pai_email.png` | `tools-reference.md` — MCP email tools |
| Network | `screenshots/pai_network.png` | `architecture.md` — Graph visualization |
| Git | `screenshots/pai_git.png` | `tools-reference.md` — Git operations |
| Dispatch | `screenshots/pai_dispatch.png` | `workflows.md` — Algorithm execution |
| Integration | `screenshots/pai_integration.png` | `architecture.md` — GitHub bridge |

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Agent Documentation**: [AGENTS.md](AGENTS.md)
- **PAI Integration**: [PAI.md](PAI.md)
- **Parent**: [docs/](../)
