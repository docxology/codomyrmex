# pai_pm — Agent Reference

## Quick Decision Tree

```
Need to check if PAI PM server is running?
  → pai_pm_health()

Need to start the server?
  → pai_pm_start()  [requires bun in PATH]

Need full project/mission state?
  → pai_pm_get_state()

Need to trigger an AI action?
  → pai_pm_dispatch(action="...", backend="claude")

Need to stop the server?
  → pai_pm_stop()
```

## When to Use MCP Tools vs CLI

| Scenario | Use |
|----------|-----|
| PAI session startup / health check | `pai_pm_health` MCP tool |
| Agent needs project context | `pai_pm_get_state` MCP tool |
| Dispatch AI task from Python | `pai_pm_dispatch` MCP tool |
| Manual server administration | `bun src/codomyrmex/pai_pm/server/server.ts` CLI |
| Adding new routes/endpoints | Edit TypeScript in `server/routes/` |

## Environment Requirements

- **bun** runtime must be in PATH (`which bun`)
- Server dependencies installed: `cd src/codomyrmex/pai_pm/server && bun install`
- `HAS_BUN` flag available: `from codomyrmex.pai_pm import HAS_BUN`

## Import Pattern

```python
from codomyrmex.pai_pm import HAS_BUN, PaiPmServerManager
from codomyrmex.pai_pm.mcp_tools import pai_pm_health, pai_pm_get_state

if HAS_BUN:
    mgr = PaiPmServerManager()
    if not mgr.is_running():
        mgr.start()
```

## Safety Notes

- `pai_pm_stop()` uses SIGTERM then SIGKILL after 5s — safe for normal shutdown.
- `_build_safe_env()` strips `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` from the subprocess env.
- All MCP tools return structured dicts and never raise — safe to call without try/except.
