# Website Handlers Agentic Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

HTTP request handler mixins for the Codomyrmex website server. Each mixin class handles a group of API endpoints, keeping the main server class thin. Agents use these handlers indirectly through the website server's routing.

## Key Components

| Component | Source | Role |
|-----------|--------|------|
| `HealthHandler` | `health_handler.py` | /api/health, /api/status, /api/telemetry, /api/security/posture, /api/awareness, /api/llm/config |
| `ProxyHandler` | `proxy_handler.py` | /api/chat (Ollama proxy), /api/awareness/summary (AI-generated) |
| `APIHandler` | `api_handler.py` | /api/modules, /api/agents, /api/scripts, /api/config, /api/docs, /api/tests, /api/pai/action, /api/agent/dispatch |

## Operating Contracts

- All handlers are mixin classes expecting the host to provide `self.data_provider`, `self.headers`, `self.rfile`, `self.send_json_response(data, status)`, and `self.send_error(code, msg)`.
- `HealthHandler` lazily initializes a shared `MetricCollector` and `DashboardManager` for telemetry.
- `ProxyHandler.handle_chat()` forwards requests to Ollama at `CODOMYRMEX_OLLAMA_URL`; returns 502/503/504 on Ollama errors.
- `APIHandler.handle_execute()` runs scripts with path traversal protection (rejects `..` in paths).
- `APIHandler.handle_tests_run()` spawns test execution in a background thread.
- `APIHandler.handle_pai_action()` dispatches PAI commands: verify, trust, reset, status, analyze, search, docs, add_memory.

## Integration Points

- Mixed into `WebsiteServer` via multiple inheritance.
- `HealthHandler` imports `SecurityDashboard` and `telemetry.dashboard` lazily.
- `ProxyHandler` uses `requests` library for Ollama HTTP calls.
- `APIHandler` delegates to `DataProvider` for all data access.

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- Parent: [website](../README.md)
