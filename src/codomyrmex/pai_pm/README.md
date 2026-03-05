# pai_pm — PAI Project Manager Module

Python wrapper for the PAI Project Manager Bun/TypeScript server. Exposes server lifecycle and REST API as MCP tools auto-discovered by the PAI MCP bridge.

## Quick Start

```bash
# Requirements: bun runtime (https://bun.sh)
cd src/codomyrmex/pai_pm/server && bun install

# Start the server via MCP tool
python -c "from codomyrmex.pai_pm.mcp_tools import pai_pm_start; print(pai_pm_start())"

# Or directly
bun src/codomyrmex/pai_pm/server/server.ts
```

## MCP Tools

| Tool | Description | Endpoint |
|------|-------------|----------|
| `pai_pm_start` | Start the PAI PM server | Subprocess |
| `pai_pm_stop` | Stop the PAI PM server | SIGTERM |
| `pai_pm_health` | Check server health | GET /api/health |
| `pai_pm_get_state` | Get dashboard state | GET /api/state |
| `pai_pm_get_awareness` | Get agent awareness | GET /api/awareness |
| `pai_pm_dispatch` | Dispatch an action | POST /api/dispatch/execute |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PAI_PM_PORT` | `8889` | Server port |
| `PAI_PM_HOST` | `127.0.0.1` | Server bind address |
| `PAI_PM_STARTUP_TIMEOUT` | `10` | Seconds to wait for server health on start |
| `PAI_PM_REQUEST_TIMEOUT` | `30` | HTTP request timeout in seconds |
| `PAI_PM_SERVER_SCRIPT` | `<module>/server/server.ts` | Path to Bun server entry point |

## Architecture

```
pai_pm/
├── __init__.py          # Module exports and HAS_BUN flag
├── config.py            # PaiPmConfig dataclass (env-var backed)
├── exceptions.py        # Exception hierarchy
├── server_manager.py    # PaiPmServerManager (Bun subprocess lifecycle)
├── client.py            # PaiPmClient (stdlib HTTP, no extra deps)
├── mcp_tools.py         # @mcp_tool definitions (auto-discovered)
└── server/              # TypeScript source (Bun runtime)
    ├── server.ts        # HTTP server entry point
    ├── config.ts        # Server configuration
    ├── routes/          # Route handlers (9 modules)
    └── services/        # OAuth and services
```

## Security

- Server subprocess inherits an allowlist env (PAI_*, GOOGLE_*, AGENTMAIL_*, PATH, HOME) — `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` are explicitly excluded.
- PID file written with `chmod 0o600`.
- Health checks use stdlib `urllib.request` only (no extra network deps).
