# PAI Scripts — scripts/pai

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Orchestration scripts for the Codomyrmex PAI ecosystem. Single entry point to set up, restart, and launch both PAI servers with browser pop-up.

## Quick Start

```bash
# Full setup + start + open browser (both servers)
uv run python scripts/pai/dashboard.py

# Kill existing servers, regenerate, restart
uv run python scripts/pai/dashboard.py --restart

# Generate static files only (no server)
uv run python scripts/pai/dashboard.py --setup-only

# Start without opening browser
uv run python scripts/pai/dashboard.py --no-open

# Skip file generation, just restart
uv run python scripts/pai/dashboard.py --no-setup --restart
```

## Scripts

| File | Description |
|------|-------------|
| `dashboard.py` | PAI dashboard orchestrator — launches both servers (:8888 + :8787) |
| `test_email_compose.py` | LLM email compose functional tests — validates all templates with real project/calendar data |
| `generate_skills.py` | Auto-generate SKILL.md files from MCP tool manifest |
| `update_pai_docs.py` | Batch update stub PAI.md files across all modules |
| `update_pai_skill.py` | Regenerate the Codomyrmex SKILL.md tool table |
| `validate_pai_integration.py` | Verify PAI integration health (thin wrapper → `codomyrmex.validation.pai`) |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       dashboard.py                          │
│  Orchestrates startup, kills stale processes, opens browser │
└───────────────────────┬─────────────────────────────────────┘
                        │ spawns
          ┌─────────────┴──────────────┐
          │                            │
          ▼                            ▼
┌─────────────────┐          ┌─────────────────────────┐
│  PMServer.ts    │          │  WebsiteServer (Python)  │
│  :8888 (bun)   │          │  :8787                   │
│  PRIMARY        │          │  ADMIN                   │
│                 │          │                           │
│  Project Mgr    │          │  Module dashboard UI      │
│  Task CRUD      │          │  Reads same data files    │
│  Dispatch jobs  │          │  Jinja2 → static HTML     │
│  Calendar auth  │          │                           │
│  Email compose  │          │                           │
└─────────────────┘          └─────────────────────────┘
        │
        └── ~/.codomyrmex/gcal_token.json
            (consumed by Codomyrmex MCP Tools)
```

Both servers read from the same underlying data files — no sync layer is needed between them.

## Ports

| Port | Server | Role | Technology |
|------|--------|------|------------|
| **8888** | PMServer.ts | Primary PAI Project Manager | Bun/TypeScript |
| **8787** | WebsiteServer | Admin module dashboard | Python/Jinja2 |

## Security

> ⚠️ **Network Exposure Warning**

By default, both servers bind to `0.0.0.0`, which means they are reachable on **all network interfaces**, including any LAN or cloud network your machine is connected to.

**Recommendations:**

- On shared or cloud environments, restrict to loopback: `--host 127.0.0.1`.
- Neither server implements an authentication layer — anyone who can reach port 8787 or 8888 can read and mutate your PAI data.
- Do not run with `0.0.0.0` binding on machines accessible from the public internet.

## Testing

```bash
# Dashboard orchestrator helpers (58 tests, see test suite)
uv run python -m pytest src/codomyrmex/tests/unit/website/test_dashboard_orchestrator.py -v

# LLM email compose (requires PMServer on :8888 + ollama)
uv run python scripts/pai/test_email_compose.py

# Dry-run (API connectivity only)
uv run python scripts/pai/test_email_compose.py --dry-run

# Full PAI/website test suite
uv run python -m pytest src/codomyrmex/tests/unit/website/ -v
```

## Troubleshooting

| Symptom | Resolution |
|---------|-----------|
| **Port already in use** | `uv run python scripts/pai/dashboard.py --restart`, or: `lsof -ti :8888 \| xargs kill -9` |
| **`bun` not found** | Install Bun: `curl -fsSL https://bun.sh/install \| bash` |
| **PMServer crashes** | Run manually: `bun ~/.claude/skills/PAI/Tools/PMServer.ts` |
| **Dashboard shows no data** | Re-run setup: `uv run python scripts/pai/dashboard.py --setup-only` |
| **`uv` not found** | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

## Related

- Primary Dashboard: `http://localhost:8888`
- Admin Dashboard: `http://localhost:8787`
- Google Calendar Auth Token: `~/.codomyrmex/gcal_token.json`
- Server implementation: `src/codomyrmex/website/server.py`
- Templates: `src/codomyrmex/website/templates/`
- PAI Bridge: `src/codomyrmex/agents/pai/`
