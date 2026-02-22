# Codomyrmex PAI Integrations (Agent Instructions)

## Objective

This directory (`scripts/pai/`) encapsulates the orchestration logic to spin up the **Personal AI (PAI) Infrastructure** and its ecosystem dashboards. Agents interacting with the PAI server should use the HTTP APIs exposed by `PMServer.ts` at `http://localhost:8888`.

## Core Orchestration

To start the PAI web servers, you should execute:

```bash
uv run python scripts/pai/dashboard.py
```

This script ensures `bun ~/.claude/skills/PAI/Tools/PMServer.ts` is running on `:8888` and the localized `WebsiteServer` admin dashboard is running on `:8787`.

## Interfacing with PAI (Agents)

You **do not** need to execute the raw Python scripts for queries. Instead, access the PAI state completely through the JSON endpoints at `http://localhost:8888`:

### 1. Data Retrieval

- `GET /api/missions`
- `GET /api/projects`
- `GET /api/tasks/summary`

### 2. State Mutation

When manipulating tasks, projects, or missions, post JSON payloads using `curl` or standard HTTP libraries.

- `POST /api/projects`
- `POST /api/tasks/{project_slug}` (Requires `text`, `priority`, `section`, etc. in JSON body).

### 3. Agentic Dispatch & AI

The PAI Server actively orchestrates multi-agent tasks (Ollama & Claude Code).

- Execute jobs: `POST /api/dispatch/execute` with a JSON payload containing `{"action": "task-implement", "context": {...}, "backend": "claude"}`.
- Query running jobs: `GET /api/dispatch/jobs`.

## Constraints & Requirements

- Always verify the server is running on `http://localhost:8888` before trying to mutate or query PM state. If not, trigger `scripts/pai/dashboard.py` in the background.
- Respect the Zero-Mock constraint: all HTTP API calls to PAI must be real, interacting with the actual filesystem backing `PMServer.ts`.
