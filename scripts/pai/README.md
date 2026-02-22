# PAI Scripts — scripts/pai

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Orchestration scripts for the Codomyrmex PAI dashboard (port 8787). Single entry point to set up, restart, and launch the dashboard with browser pop-up.

## Quick Start

```bash
# Full setup + start + open browser
uv run python scripts/pai/dashboard.py

# Kill existing server, regenerate, restart, open browser
uv run python scripts/pai/dashboard.py --restart

# Generate static files only (no server)
uv run python scripts/pai/dashboard.py --setup-only

# Start server without opening browser
uv run python scripts/pai/dashboard.py --no-open

# Skip file generation, just restart the server
uv run python scripts/pai/dashboard.py --no-setup --restart
```

## Scripts

| File | Description |
|------|-------------|
| `dashboard.py` | PAI dashboard orchestrator — setup, restart, and launch |

## What `dashboard.py` Does

Three sequential phases:

1. **RESTART** (optional `--restart`): Finds and kills any process on port 8787 via `lsof` + SIGTERM/SIGKILL.
2. **SETUP** (skippable with `--no-setup`): Runs `WebsiteGenerator` to render all Jinja2 templates to `output/website/`, writes root `index.html` redirect.
3. **RUN**: Initialises `DataProvider`, binds `WebsiteServer` on the requested port, opens browser after 1.2s delay.

## Related

- Dashboard URL: `http://localhost:8787`
- PAI Project Manager: `http://localhost:8888` (`bun ~/.claude/skills/PAI/Tools/PMServer.ts`)
- Server implementation: `src/codomyrmex/website/server.py`
- Templates: `src/codomyrmex/website/templates/`
