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

### Email Integration

#### AgentMail

- **`GET /api/email/agentmail/status`**: Returns connection status and available inboxes (`{ success, inboxes: [{ inbox_id, display_name }] }`).
- **`GET /api/email/agentmail/messages`**: Lists messages in the AgentMail inbox.
- **`POST /api/email/agentmail/send`**: Sends an email via AgentMail. Requires `{ to, subject, body }`.

#### Gmail

- **`GET /api/email/gmail/messages`**: Lists recent Gmail messages (requires OAuth token at `~/.codomyrmex/gcal_token.json`).
- **`GET /api/email/gmail/thread/{threadId}`**: Returns the full thread for a specific Gmail thread ID.
- **`POST /api/email/gmail/send`**: Sends an email via the authenticated Gmail account. Requires `{ to, subject, body }`.
- **`DELETE /api/email/gmail/disconnect`**: Disconnects the Gmail OAuth session.

### LLM Email Compose

- **`POST /api/email/compose`**: Generates a context-driven email using an LLM backend. Gathers real project, mission, task, and calendar data, then sends it to the selected LLM with a template-specific prompt.

  **Request body:**

  ```json
  {
    "template": "daily-schedule",
    "backend": "ollama",
    "model": "llama3.2",
    "project": "optional-project-slug",
    "customPrompt": "optional custom instructions"
  }
  ```

  **Templates:**

  | Template | Purpose | Context Gathered |
  |----------|---------|-----------------|
  | `daily-schedule` | Today's calendar + active tasks | Calendar events (today/tomorrow), in-progress tasks only |
  | `all-projects` | Cross-project status summary | All missions, all projects with full task breakdowns |
  | `project-summary` | Single project deep-dive | Selected project with all tasks grouped by section |
  | `interview-followup` | Interview follow-up email | Project context + current date |
  | `custom` | Free-form with custom prompt | All available context + user prompt |

  **Response (200):**

  ```json
  {
    "success": true,
    "subject": "Daily Schedule — 2/28/2026",
    "body": "1. Today's Calendar\n- 09:00 AM - PAI Interview...",
    "to": "",
    "template": "daily-schedule",
    "backend": "ollama"
  }
  ```

### Calendar Integration

- **`GET /api/calendar/events`**: Returns Google Calendar events from the authenticated account (requires OAuth token).
- **`POST /api/calendar/events`**: Creates a new Google Calendar event. Requires `{ summary, startTime, endTime, description?, location?, attendees? }`.
- **`POST /api/calendar/sync-deadlines`**: Synchronizes PAI project deadlines to Google Calendar.

## Error Response Schema

All error responses follow a consistent JSON format:

```json
{
  "success": false,
  "error": "Human-readable error description"
}
```

| Code | Meaning | Common Cause |
|------|---------|-------------|
| `200` | OK | Request succeeded |
| `400` | Bad Request | Missing required fields or invalid template name |
| `401` | Unauthorized | Missing or invalid OAuth token |
| `404` | Not Found | Project slug, task ID, or draft ID not found |
| `409` | Conflict | Duplicate slug on project creation |
| `500` | Internal Error | PMServer or LLM backend exception |
| `504` | Gateway Timeout | LLM backend (Ollama/Claude) did not respond within timeout |

## Rate Limiting & Timeouts

| Endpoint | Timeout | Notes |
|----------|---------|-------|
| `POST /api/email/compose` | 120s | LLM inference may take 30–90s depending on model and backend |
| `POST /api/dispatch/execute` | 300s | Agentic dispatch jobs are streamed via WebSocket |
| All other endpoints | 30s | Standard HTTP timeout |
