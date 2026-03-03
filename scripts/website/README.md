# Website Scripts

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

Scripts for launching and working with the Codomyrmex Web Dashboard.

## Quick Start

```bash
# Install dependencies
uv sync

# Launch dashboard (generates static files, starts server, opens browser)
python scripts/website/launch_dashboard.py --open

# Custom port
python scripts/website/launch_dashboard.py --port 8000 --open

# Or via CLI shortcut
codomyrmex dashboard --open
```

## Launch Script: `launch_dashboard.py`

The primary entry point for the Codomyrmex website. It:
1. Generates static HTML pages from Jinja2 templates into `output/website/`
2. Creates a root redirect at `index.html`
3. Initializes the `DataProvider` (module discovery, git status, PAI awareness)
4. Starts the REST API server at the specified port
5. Optionally opens the browser automatically

### CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--port PORT` | `8787` | Port to serve on |
| `--host HOST` | `0.0.0.0` | Host to bind to |
| `--open` | off | Open browser automatically after start |

### Dashboard Pages

After launch, open `http://localhost:8787` — it redirects to the generated dashboard.

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/output/website/index.html` | System metrics, MCP status, quick actions |
| Health | `/output/website/health.html` | Vitals, git, coverage bars, test runner, security posture |
| Modules | `/output/website/modules.html` | All 89+ modules with status badges |
| Tools | `/output/website/tools.html` | MCP tools, resources, prompts |
| Scripts | `/output/website/scripts.html` | Browser-executable scripts |
| Config | `/output/website/config.html` | Config file editor |
| Docs | `/output/website/docs.html` | README/SPEC/AGENTS browser |
| Pipelines | `/output/website/pipelines.html` | CI/CD workflow status |
| Agents | `/output/website/agents.html` | AI agent integrations |
| Chat | `/output/website/chat.html` | Ollama LLM chat interface |
| Awareness | `/output/website/awareness.html` | PAI missions, projects, tasks, Mermaid graph |
| PAI Control | `/output/website/pai_control.html` | Trust management, workflow actions |
| Dispatch | `/output/website/dispatch.html` | Agent orchestrator dispatch |
| Telemetry | `/output/website/telemetry.html` | Metric series, dashboard registry |

### API Endpoints

The server exposes 27 REST endpoints at `http://localhost:8787/api/...`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | System summary metrics |
| `/api/health` | GET | Comprehensive health data |
| `/api/modules` | GET | List all modules |
| `/api/modules/{name}` | GET | Module detail |
| `/api/agents` | GET | List AI agent integrations |
| `/api/scripts` | GET | List available scripts |
| `/api/config` | GET | List configuration files |
| `/api/config/{name}` | GET | Read config file content |
| `/api/config` | POST | Save config file content |
| `/api/docs` | GET | Documentation tree |
| `/api/docs/{path}` | GET | Doc file content |
| `/api/pipelines` | GET | CI/CD pipeline status |
| `/api/awareness` | GET | PAI ecosystem data |
| `/api/awareness/summary` | POST | Generate Ollama AI summary |
| `/api/execute` | POST | Run a script |
| `/api/chat` | POST | Proxy to Ollama |
| `/api/tests` | POST | Run pytest suite |
| `/api/refresh` | POST | Refresh system data |
| `/api/llm/config` | GET | Retrieve LLM configuration |
| `/api/tools` | GET | MCP tools, resources, prompts |
| `/api/trust/status` | GET | Trust gateway counts + destructive tools |
| `/api/pai/action` | POST | Execute PAI action (verify/trust/reset/status) |
| `/api/agent/dispatch` | POST | Start an orchestrator run |
| `/api/agent/dispatch/status` | GET | Poll orchestrator transcript |
| `/api/agent/dispatch/stop` | POST | Stop orchestrator run |
| `/api/telemetry` | GET | Telemetry metric series and dashboard registry |
| `/api/security/posture` | GET | Security posture: risk score, compliance rate |

## Other Scripts

| Script | Description |
|--------|-------------|
| `orchestrate.py` | Demonstration of the ConversationOrchestrator multi-agent workflow |
| `website_utils.py` | Helper utilities for website operations |

## Related PAI Dashboards

| Dashboard | Port | Start Command |
|-----------|------|---------------|
| **This dashboard** (Codomyrmex) | 8787 | `python scripts/website/launch_dashboard.py --open` |
| **PAI Observability** | 5172 + 4000 | `~/.claude/Observability/scripts/start-agent-observability-dashboard.sh` |
| **PAI Project Manager** | 8889 | `bun ~/.claude/skills/PAI/Tools/PMServer.ts` |
| **MCP HTTP Server** | 8080 | `python scripts/model_context_protocol/run_mcp_server.py --transport http` |

> **Port note**: PAI VoiceServer uses port 8888. PMServer now defaults to port 8889 to avoid conflict. Both can run simultaneously.

## Prerequisites

```bash
uv sync          # Core dependencies
uv sync --all-extras  # All optional module dependencies
```

## Navigation

- [Module Source](../../src/codomyrmex/website/)
- [PAI Integration](PAI.md)
- [SPEC](SPEC.md)
- [Parent scripts/](../README.md)
