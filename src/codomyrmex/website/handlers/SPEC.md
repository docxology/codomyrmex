# Website Handlers -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Three mixin classes that decompose the website server's HTTP API into functional groups: health/telemetry, Ollama proxy, and general API endpoints. Each mixin is stateless except for `HealthHandler`'s shared telemetry collector.

## Architecture

```
WebsiteServer (BaseHTTPRequestHandler)
  inherits: HealthHandler, ProxyHandler, APIHandler

HealthHandler (mixin)
  +-- handle_status()            -> /api/status
  +-- handle_health()            -> /api/health
  +-- handle_awareness()         -> /api/awareness
  +-- handle_llm_config()        -> /api/llm/config
  +-- handle_telemetry()         -> /api/telemetry
  +-- handle_telemetry_seed()    -> /api/telemetry/seed (POST)
  +-- handle_security_posture()  -> /api/security/posture

ProxyHandler (mixin)
  +-- handle_chat()              -> /api/chat (POST)
  +-- handle_awareness_summary() -> /api/awareness/summary (POST)

APIHandler (mixin)
  +-- handle_modules_list()      -> /api/modules
  +-- handle_module_detail()     -> /api/modules/{name}
  +-- handle_tools_list()        -> /api/tools
  +-- handle_agents_list()       -> /api/agents
  +-- handle_scripts_list()      -> /api/scripts
  +-- handle_config_list/get/save() -> /api/config
  +-- handle_docs_list/get()     -> /api/docs
  +-- handle_execute()           -> /api/execute (POST)
  +-- handle_tests_run/status()  -> /api/tests
  +-- handle_pai_action()        -> /api/pai/action (POST)
  +-- handle_agent_dispatch/stop/status() -> /api/agent/*
```

## Key Endpoints

### HealthHandler

| Endpoint | Method | Response |
|----------|--------|----------|
| `/api/status` | GET | System summary from DataProvider |
| `/api/health` | GET | Comprehensive health data |
| `/api/telemetry` | GET | Metric series, dashboards, latest values |
| `/api/telemetry/seed` | POST | Seed baseline metrics (module/tool/agent counts) |
| `/api/security/posture` | GET | Risk score, compliance rate, secret findings |

### ProxyHandler

| Endpoint | Method | Response |
|----------|--------|----------|
| `/api/chat` | POST | Proxied Ollama chat completion |
| `/api/awareness/summary` | POST | AI-generated PAI ecosystem summary |

### APIHandler

| Endpoint | Method | Response |
|----------|--------|----------|
| `/api/modules` | GET | List all discovered modules |
| `/api/execute` | POST | Run script with path traversal protection |
| `/api/tests/run` | POST | Start test execution (background thread) |
| `/api/pai/action` | POST | Dispatch PAI commands (verify/trust/reset/...) |

## Dependencies

- `requests` for Ollama HTTP proxy
- `codomyrmex.telemetry.dashboard` (lazy import in HealthHandler)
- `codomyrmex.security.dashboard` (lazy import for posture)
- `codomyrmex.config_management.defaults` for Ollama URL/model defaults

## Constraints

- Telemetry collector is class-level shared state (`_telemetry_collector`); not thread-safe for concurrent writes.
- Ollama proxy timeout is 60 seconds; not configurable per-request.
- Script execution in `handle_execute` validates paths but runs subprocess directly.
- Test execution runs in a daemon thread; results polled via `/api/tests/status`.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- Parent: [website](../README.md)
