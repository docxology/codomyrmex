# Codomyrmex PAI Specification

## Purpose

This specification details the expected behavior and HTTP interface definitions for the `scripts/pai/` orchestrator and the underlying `PMServer.ts` PAI system.

## Architectural Constraints

- **Double Binding**: The `scripts/pai/dashboard.py` daemon must guarantee that both `PMServer.ts` (`:8888`) and `WebsiteServer` (`:8787`) are operational.
- **REST Compliance**: The `PMServer.ts` must expose fully functional GET, POST, PUT, and DELETE handlers conforming to standard application/json signatures.

## HTTP API Specification (`http://localhost:8888`)

### Mission Management

- **`GET /api/missions`**: Lists all active and archived missions.
- **`POST /api/missions`**: Creates a new mission requiring `{ slug, title, description, vision, status }`.
- **`PUT /api/missions/{slug}`**: Mutates an existing mission state or relationships.
- **`DELETE /api/missions/{slug}`**: Hard deletes a mission folder.

### Project Management

- **`GET /api/projects`**: Lists all projects, filterable by `status`.
- **`GET /api/projects/{slug}`**: Details the project board, Kanban lanes, and blocking tasks.
- **`POST /api/projects`**: Scaffolds a new project directory with standard properties.
- **`POST /api/projects/{slug}/complete`**: Finalizes the project state and clears blockers.

### Task Management

- **`GET /api/tasks`**: Returns filterable lists of nested tasks across projects.
- **`POST /api/tasks/{project_slug}`**: Issues a new task instruction inside the specified project context.
- **`PUT /api/tasks/{project_slug}/{task_text}`**: Updates task status, priority, or mappings.

### GitHub Synchronisation

- **`POST /api/github/sync`**: Executes a bidirectional GitHub issue synchronization job for tracked projects.
- **`GET /api/github/status`**: Yields the repository mapping validation.

### Dispatch Ecosystem

- **`POST /api/dispatch/execute`**: Asynchronously dispatches a cognitive workload (`claude` or `ollama` backends) to solve the specific bounded context defined in the payload. Streamed output events are broadcast via WebSocket.
- **`GET /api/dispatch/jobs`**: Obtains execution manifests and status reports for recent agentic dispatches.
