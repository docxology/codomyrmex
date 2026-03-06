# docs/pai — Functional Specification

**Version**: v1.1.6 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Expanded reference documentation for the PAI-Codomyrmex integration. Supplements the root `PAI.md` bridge document with detailed architecture, API, and tool references. The PAI Command Center (port 8888) is a 15-tab modular SPA served from `src/codomyrmex/agents/pai/pm/`.

![PAI Analytics — Primary dashboard interface showing mission, project, and task metrics](screenshots/pai_analytics.png)

## Scope

| Document | Covers |
|----------|--------|
| `README.md` | Index with full 15-tab screenshot gallery |
| `architecture.md` | Component diagram, data flow, trust model, cross-language communication |
| `dashboard-setup.md` | Both dashboards (:8787 + :8888), modular server architecture, all API endpoints |
| `tools-reference.md` | All 22 static tools with parameters, trust levels; dynamic discovery mechanism |
| `api-reference.md` | PAIBridge (24 methods), TrustRegistry, module functions, dataclasses, constants |
| `workflows.md` | `/codomyrmexVerify`, `/codomyrmexTrust`, Algorithm phase mapping |
| `skills-and-commands.md` | External Claude Code skills (visual-explainer, slash commands) |
| `screenshots/` | PAI Dashboard interface screenshots (15 tabs + 1 WebP tour) |

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

### PAI Command Center (port 8888)

Started with: `uv run python scripts/pai/dashboard.py` or `bun run src/codomyrmex/agents/pai/pm/server.ts`

**Server**: `src/codomyrmex/agents/pai/pm/server.ts` (TypeScript/Bun, modular routes)

| Tab | Purpose | Screenshot |
|-----|---------|------------|
| Analytics | Mission/project/task KPIs, status/priority charts, completion bars | `pai_analytics.png` |
| Awareness | PAI awareness data — mission/project context | `pai_awareness.png` |
| Blockers | Blocked items and dependency tracking | `pai_blockers.png` |
| Board | Kanban with drag-drop: ACTIVE → PLANNING → IN PROGRESS → BLOCKED → COMPLETED | `pai_board.png` |
| Calendar | Google Calendar OAuth integration, event creation | `pai_calendar.png` |
| Email | AgentMail + Gmail dual-provider, LLM-assisted compose | `pai_email.png` |
| Data | Full CRUD tables for missions, projects, tasks with filters | `pai_data.png` |
| Dispatch | Algorithm execution: Summarize, Scope & Plan, Review, Enact | `pai_dispatch.png` |
| Git | Repository sync — push/pull/sync per project | `pai_git.png` |
| Integration | GitHub bridge, issue tracking, JSON/CSV export | `pai_integration.png` |
| Interview | Task specification interviews | `pai_interview.png` |
| Network | Force-directed mission→project→task graph | `pai_network.png` |
| Projects | Per-project drill-down view | `pai_projects.png` |
| Timeline | Temporal Gantt-style project visualization | `pai_timeline.png` |
| 🚴 Bike Ride | LLM email briefing — unanswered threads + A/B/C drafts + TTS | `pai_bikeride.png` |

### MCP Tool Counts (v1.1.6)

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
5. **Modular**: PM server codebase split into routes/, services/, spa/ — not monolithic

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Agent Documentation**: [AGENTS.md](AGENTS.md)
- **PAI Integration**: [PAI.md](PAI.md)
- **Dashboard Setup**: [dashboard-setup.md](dashboard-setup.md)
- **Parent**: [docs/](../)
