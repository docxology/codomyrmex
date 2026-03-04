# Dashboard Setup Guide

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

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
| **Modules** | `/modules` | All 127 modules with status (Active / ImportError / SyntaxError) |
| **Agents** | `/agents` | AI agent integrations (Claude, Jules, Codex, Aider, etc.) |
| **Scripts** | `/scripts` | Executable scripts in `scripts/`; run them with args from UI |
| **Config** | `/config` | Read/edit `.json`, `.toml`, `.yaml` config files |
| **Docs** | `/docs` | Browse `docs/` directory and module READMEs |
| **Tools** | `/tools` | All ~407 MCP tools with trust classification (safe / destructive) |
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

A TypeScript/Bun dashboard for managing PAI missions, projects, and tasks.

### Starting

```bash
# Requires Bun and PAI v4+:
bun run ~/.claude/PAI/Tools/PMServer.ts

# Then open:
open http://localhost:8888/
```

### Tabs

| Tab | Purpose |
|-----|---------|
| **Analytics** | Mission/project KPIs, completion rates, status badges |
| **Board** | Kanban: ACTIVE, PLANNING, IN PROGRESS, BLOCKED, PAUSED |
| **Calendar** | Google Calendar integration, event creation |
| **Email** | AgentMail + Gmail dual-provider, AI-assisted drafting |
| **Network** | Force-directed mission→project→task relationship graph |
| **Git** | Repository sync, branch management |
| **Dispatch** | Algorithm phase execution (Summarize, Scope & Plan, Review, Enact) |
| **Integration** | GitHub bridge, PR/issue tracking |

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
