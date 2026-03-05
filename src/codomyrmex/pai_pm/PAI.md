# pai_pm — PAI Integration Reference

## MCP Tools

| Tool | Description |
|------|-------------|
| `pai_pm_start` | Start the PAI PM server subprocess |
| `pai_pm_stop` | Stop the PAI PM server |
| `pai_pm_health` | Check server health (returns `running: bool`) |
| `pai_pm_get_state` | Fetch full dashboard state (missions, projects, tasks) |
| `pai_pm_get_awareness` | Fetch agent awareness context |
| `pai_pm_dispatch` | Dispatch an action for AI execution |

## PAI Algorithm Phase Mapping

| Phase | pai_pm Tools | Use Case |
|-------|-------------|---------|
| **OBSERVE** | `pai_pm_health`, `pai_pm_get_state` | Check server status; load project/mission context |
| **THINK** | `pai_pm_get_awareness` | Load current work priorities and active missions |
| **PLAN** | `pai_pm_get_state` | Read project structure to plan task breakdown |
| **BUILD** | `pai_pm_dispatch` | Dispatch coding/analysis actions to AI backends |
| **EXECUTE** | `pai_pm_dispatch`, `pai_pm_get_state` | Execute dispatched actions; poll for state changes |
| **VERIFY** | `pai_pm_get_state`, `pai_pm_health` | Confirm task completion state; verify server healthy |
| **LEARN** | `pai_pm_get_state` | Read final state for reflection and journaling |

## Server Lifecycle

```
OBSERVE: pai_pm_health()
  ↓ not running
pai_pm_start()
  ↓
pai_pm_get_state()  → context loaded
  ↓
[algorithm runs]
  ↓
pai_pm_stop()  [optional — server persists across sessions]
```

## Integration Notes

- Auto-discovered by PAI MCP bridge via `@mcp_tool` in `mcp_tools.py` — no manual registration needed.
- Server runs on `http://127.0.0.1:8889` by default — configurable via `PAI_PM_PORT`.
- TypeScript source lives in `server/` subdirectory — Python wrapper delegates all HTTP calls via `PaiPmClient`.
- `HAS_BUN` flag gates all server operations: `from codomyrmex.pai_pm import HAS_BUN`.
