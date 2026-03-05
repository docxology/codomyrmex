# PAI PM Server — Thin Pointer

> **All code has been moved to the canonical module location.**
>
> **Source:** [`src/codomyrmex/agents/pai/pm/`](../../../src/codomyrmex/agents/pai/pm/)

## Quick Reference

```bash
# Start the modular PM server directly
bun src/codomyrmex/agents/pai/pm/server.ts --port 8888

# Or via the dashboard orchestrator (recommended)
uv run python scripts/pai/dashboard.py --restart
```

## What Moved

| Component | New Location |
|-----------|-------------|
| `server.ts` | `src/codomyrmex/agents/pai/pm/server.ts` |
| `PMDashboard.ts` | `src/codomyrmex/agents/pai/pm/PMDashboard.ts` |
| `routes/*.ts` | `src/codomyrmex/agents/pai/pm/routes/` |
| `services/*.ts` | `src/codomyrmex/agents/pai/pm/services/` |
| All CRUD tools | `src/codomyrmex/agents/pai/pm/` |
| `config.ts`, `helpers.ts` | `src/codomyrmex/agents/pai/pm/` |
