# Website Handlers

> **Codomyrmex v1.1.9** | Sub-module of `website` | March 2026

## Overview

The `handlers` sub-module contains the HTTP endpoint handler mixins used by
`WebsiteServer`. Each handler class is mixed into the main request handler to
separate concerns: API endpoints for modules, agents, scripts, config, docs,
pipelines, tools, tests, and PAI actions live in `APIHandler`; health, status,
telemetry, and security posture live in `HealthHandler`; and Ollama chat proxy
plus AI-powered summaries live in `ProxyHandler`.

This package was extracted from the monolithic `server.py` during a prior
refactoring sprint to keep each handler class focused and testable.

## PAI Integration

| PAI Phase | Usage |
|-----------|-------|
| OBSERVE   | `/api/status`, `/api/health`, `/api/awareness` endpoints |
| EXECUTE   | `/api/agents/dispatch`, `/api/tests/run`, `/api/scripts/run` |
| BUILD     | `/api/chat` Ollama proxy for code generation assistance |

## Key Exports

| Export | Source | Description |
|--------|--------|-------------|
| `APIHandler` | `api_handler.py` | Mixin for `/api/*` routes: modules, agents, scripts, config, docs, pipelines, tools, tests, PAI actions |
| `HealthHandler` | `health_handler.py` | Mixin for `/api/health`, `/api/status`, `/api/telemetry`, `/api/security/posture`, `/api/awareness` |
| `ProxyHandler` | `proxy_handler.py` | Mixin for `/api/chat` (Ollama proxy) and `/api/awareness/summary` (AI summary generation) |

## Architecture

```
website/handlers/
  __init__.py          # Re-exports APIHandler, HealthHandler, ProxyHandler
  api_handler.py       # /api/* endpoint handlers (modules, agents, tools, tests, etc.)
  health_handler.py    # Health, status, telemetry, security posture, PAI awareness
  proxy_handler.py     # Ollama chat proxy and AI-powered summary generation
```

## Handler Details

### APIHandler (`api_handler.py`)

Handles the core data endpoints:

- `handle_modules_list` -- `GET /api/modules`
- `handle_module_detail` -- `GET /api/modules/{name}`
- `handle_tools_list` -- `GET /api/tools`
- `handle_agents_list` -- `GET /api/agents`
- `handle_scripts_list` -- `GET /api/scripts`
- `handle_config` -- `GET /api/config`
- `handle_docs` -- `GET /api/docs`
- `handle_tests_run` -- `POST /api/tests/run`
- `handle_pai_action` -- `POST /api/pai/action`
- `handle_agent_dispatch` -- `POST /api/agents/dispatch`

### HealthHandler (`health_handler.py`)

Handles observability endpoints:

- `handle_health` -- `GET /api/health`
- `handle_status` -- `GET /api/status`
- `handle_awareness` -- `GET /api/awareness`
- `handle_telemetry` -- `GET /api/telemetry`
- `handle_security_posture` -- `GET /api/security/posture`

### ProxyHandler (`proxy_handler.py`)

Handles AI proxy endpoints:

- `handle_chat` -- `POST /api/chat` (proxies to Ollama at `CODOMYRMEX_OLLAMA_URL`)
- `handle_awareness_summary` -- `POST /api/awareness/summary` (generates AI summaries)

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/website/ -v
```

## Navigation

| Document | Purpose |
|----------|---------|
| [AGENTS.md](AGENTS.md) | Agent coordination guidance |
| [SPEC.md](SPEC.md) | Technical specification |
| [Parent README](../README.md) | `website` module overview |
