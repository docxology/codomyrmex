# pai_pm — API Specification

## MCP Tool Schemas

### `pai_pm_start`

**Input:** _(no parameters)_

**Output:**
```json
{
  "status": "started" | "already_running" | "error",
  "pid": 12345,
  "port": 8889,
  "host": "127.0.0.1"
}
```

**Error output:**
```json
{"status": "error", "message": "bun runtime not found in PATH. Install from https://bun.sh"}
```

---

### `pai_pm_stop`

**Input:** _(no parameters)_

**Output:**
```json
{"status": "stopped" | "not_running", "pid": 12345}
```

---

### `pai_pm_health`

**Input:** _(no parameters)_

**Output (running):**
```json
{"running": true, "status": "ok", "port": 8889, "uptime": 42.3}
```

**Output (not running):**
```json
{"running": false}
```

---

### `pai_pm_get_state`

**Input:** _(no parameters)_

**Output:** Full dashboard data from `/api/state`:
```json
{"missions": [...], "projects": [...], "orphan_projects": [...], "stats": {...}}
```

---

### `pai_pm_get_awareness`

**Input:** _(no parameters)_

**Output:** Agent awareness context from `/api/awareness`.

---

### `pai_pm_dispatch`

**Input:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `action` | `str` | Yes | — | Action name to dispatch |
| `backend` | `str` | No | `""` | Backend (e.g. `claude`, `gemini`) |
| `model` | `str` | No | `""` | Model override |
| `context` | `dict` | No | `null` | Context passed to the action |

**Output:** Dispatch result or job reference dict.

---

## Error Taxonomy

| Exception | Condition |
|-----------|-----------|
| `PaiPmNotInstalledError` | `bun` not found in `PATH` |
| `PaiPmServerError` | Server failed to start or become healthy |
| `PaiPmTimeoutError` | HTTP request timed out |
| `PaiPmConnectionError` | Server not running or unreachable |

All MCP tools catch all exceptions and return `{"status": "error", "message": str(exc)}` — tools never raise.

## State Machine

```
NOT_RUNNING ──pai_pm_start──► STARTING ──healthy──► RUNNING
RUNNING ──pai_pm_stop──► NOT_RUNNING
STARTING ──timeout──► NOT_RUNNING (PaiPmServerError raised)
```

## Endpoint Mapping

| MCP Tool | HTTP Method | Path |
|----------|-------------|------|
| `pai_pm_health` | GET | `/api/health` |
| `pai_pm_get_state` | GET | `/api/state` |
| `pai_pm_get_awareness` | GET | `/api/awareness` |
| `pai_pm_dispatch` | POST | `/api/dispatch/execute` |
| `list_missions` (client) | GET | `/api/missions` |
| `list_projects` (client) | GET | `/api/projects` |
| `list_tasks` (client) | GET | `/api/projects/:slug/tasks` |
