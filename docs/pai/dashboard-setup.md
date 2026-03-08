# Dashboard Setup Guide

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

Two dashboards exist in the PAI-Codomyrmex ecosystem. They serve different purposes and run on different ports.

---

## Codomyrmex Admin Dashboard (port 8787)

A Python/HTTP dashboard for inspecting and operating the codomyrmex module ecosystem.

### Starting

```bash
# From the codomyrmex repo root:
uv run python -m codomyrmex.website.server

# Or via the launch script:
uv run python scripts/website/launch_dashboard.py

# Then open:
open http://localhost:8787/
```

### Tabs

| Tab | URL | What It Shows |
|-----|-----|---------------|
| **Overview** | `/` | System status, module count, uptime, git branch, coverage |
| **Modules** | `/modules` | All 128 modules with status (Active / ImportError / SyntaxError) |
| **Agents** | `/agents` | AI agent integrations (Claude, Jules, Codex, Aider, etc.) |
| **Scripts** | `/scripts` | Executable scripts in `scripts/`; run them with args from UI |
| **Config** | `/config` | Read/edit `.json`, `.toml`, `.yaml` config files |
| **Docs** | `/docs` | Browse `docs/` directory and module READMEs |
| **Tools** | `/tools` | All ~474 MCP tools with trust classification (safe / destructive) |
| **Tests** | `/tests` | Run pytest async; poll for results; view JUnit XML summary |
| **Chat** | `/chat` | Direct LLM chat via Ollama (requires Ollama running) |
| **Health** | `/health` | Python version, architecture layers, git status, pipeline status |
| **Telemetry** | `/telemetry` | In-process time-series metrics (module count, tool count, etc.) |
| **PAI Control** | `/awareness` | PAI missions, projects, tasks, TELOS, memory directory counts |
| **Dispatch** | `/dispatch` | Start/stop `ConversationOrchestrator`; view live agent transcript |

### Keyboard Shortcuts

| Shortcut | Tab |
|----------|-----|
| Alt+1 | Overview |
| Alt+2 | Modules |
| Alt+3 | Agents |
| Alt+4 | Scripts |
| Alt+5 | Config |
| Alt+6 | Docs |
| Alt+7 | Tools |
| Alt+8 | Tests |
| Alt+9 | Chat |

### Environment Variables

| Variable | Default | Effect |
|----------|---------|--------|
| `CODOMYRMEX_DASHBOARD_PORT` | `8787` | HTTP listen port |
| `CODOMYRMEX_DASHBOARD_HOST` | `localhost` | Bind address |
| `CODOMYRMEX_CORS_ORIGINS` | `localhost:8787,8888,8889` | Allowed CORS origins |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API for chat tab |

### Security Model

- **No authentication by design** — assumes trusted local network access
- **CORS origin validation**: only allowed origins can POST (prevents drive-by CSRF)
- **Path traversal protection**: all file reads/writes resolve and check against project root
- **Shell injection protection**: script args validated against metacharacter blocklist
- **ReDoS protection**: search queries run through `re.escape()` before compilation

---

## PAI Project Manager Dashboard (port 8888)

A TypeScript/Bun dashboard for managing PAI missions, projects, and tasks. The modular server lives in `src/codomyrmex/agents/pai/pm/` with route handlers split into separate files under `routes/`.

### Starting

```bash
# Recommended — launches both dashboards (:8787 + :8888):
uv run python scripts/pai/dashboard.py

# Or start the PM server directly:
bun run src/codomyrmex/agents/pai/pm/server.ts

# Then open:
open http://localhost:8888/
```

### 15 Interface Tabs

| Tab | Purpose |
|-----|---------|
| **Analytics** | Mission/project/task KPIs, status/priority charts, completion bars |
| **Awareness** | PAI awareness data — mission/project context and system state |
| **Blockers** | Blocked items and dependency tracking |
| **Board** | Kanban: ACTIVE, PLANNING, IN PROGRESS, BLOCKED, PAUSED, COMPLETED |
| **Calendar** | Google Calendar integration, event creation, attendee management |
| **Email** | AgentMail + Gmail dual-provider, AI-assisted compose (ollama/gemini/claude) |
| **Data** | Full CRUD tables — Missions (7), Projects (19), Tasks (831) with status badges |
| **Dispatch** | Algorithm phase execution (Summarize, Scope & Plan, Review, Enact) |
| **Git** | Repository sync, branch management, push/pull/unlink per project |
| **Integration** | GitHub bridge, PR/issue tracking, JSON/CSV data export |
| **Interview** | Task specification interviews for requirement gathering |
| **Network** | Force-directed mission→project→task graph visualization |
| **Projects** | Per-project drill-down with task breakdown |
| **Timeline** | Temporal project view with Gantt-style visualization |
| **🚴 Bike Ride** | LLM-powered email briefing — unanswered Gmail threads, A/B/C drafts, TTS |

### Modular Server Architecture

```
src/codomyrmex/agents/pai/pm/
├── server.ts           # Bun HTTP server entry point
├── config.ts           # Port, paths, environment
├── helpers.ts          # Utility functions (JSON, CORS, parsing)
├── PMDashboard.ts      # Dashboard HTML generator (fallback)
├── spa/
│   └── index.html      # Full 15-tab SPA (served as static file)
├── routes/
│   ├── missions.ts     # /api/missions CRUD
│   ├── projects.ts     # /api/projects CRUD
│   ├── tasks.ts        # /api/tasks CRUD
│   ├── github.ts       # /api/github/* sync
│   ├── dispatch.ts     # /api/dispatch/*
│   ├── interview.ts    # /api/interview/*
│   ├── awareness.ts    # /api/awareness
│   ├── calendar.ts     # /api/calendar/* (Google Calendar OAuth)
│   └── email.ts        # /api/email/*, /api/bikeride/*
└── services/
    └── oauth.ts        # Gmail/Calendar OAuth helpers
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Server health check |
| `/api/awareness` | GET | Full PAI awareness data |
| `/api/missions` | GET/POST/PUT/DELETE | Mission CRUD |
| `/api/projects` | GET/POST/PUT/DELETE | Project CRUD |
| `/api/tasks` | GET/POST/PUT/DELETE | Task CRUD |
| `/api/github/sync` | POST | GitHub repository sync |
| `/api/dispatch/execute` | POST | Algorithm phase execution |
| `/api/interview/start` | POST | Task specification interview |
| `/api/calendar/*` | GET/POST | Google Calendar integration |
| `/api/email/compose` | POST | LLM-powered email drafting |
| `/api/bikeride/load` | POST | Load unanswered Gmail threads + generate drafts |
| `/api/bikeride/send` | POST | Send a selected draft reply |
| `/api/bikeride/tts` | POST | Text-to-speech for email briefings |

---

## Connecting Both Dashboards

The two dashboards are independent but share data:

```
PAI Dashboard (8888)              Codomyrmex Dashboard (8787)
   TypeScript/Bun                       Python/HTTP
   PAI missions & tasks  <—MCP—>    Module tools & execution
   ~/.claude/MEMORY/               src/codomyrmex/
```

The Codomyrmex Admin's **PAI Control** tab reads from `~/.claude/` to surface PAI missions and tasks alongside module status — giving a unified view without running both dashboards simultaneously.

---

## Signposting

- **Self**: [dashboard-setup.md](dashboard-setup.md)
- **Architecture**: [architecture.md](architecture.md)
- **Tool Reference**: [tools-reference.md](tools-reference.md)
- **Root Bridge**: [../../PAI.md](../../PAI.md)
