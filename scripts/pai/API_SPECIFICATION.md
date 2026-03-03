# PAI API Specification

**Version**: v1.0.0 | **Base URL**: `http://localhost:8888`

## Authentication

No authentication layer. All endpoints are accessible without credentials. Network-level access control is the only security boundary.

## Content Type

All endpoints accept and return `application/json`.

---

## Endpoints

### Missions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/missions` | List all missions |
| POST | `/api/missions` | Create a mission |
| PUT | `/api/missions/{slug}` | Update a mission |
| DELETE | `/api/missions/{slug}` | Delete a mission |

### Projects

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/projects` | List all projects |
| GET | `/api/projects/{slug}` | Get project details |
| POST | `/api/projects` | Create a project |
| POST | `/api/projects/{slug}/complete` | Complete a project |

### Tasks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tasks` | List all tasks |
| GET | `/api/tasks/summary` | Task summary stats |
| POST | `/api/tasks/{project_slug}` | Create a task |
| PUT | `/api/tasks/{project_slug}/{task_text}` | Update a task |

### Calendar

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/calendar/events` | List calendar events |
| POST | `/api/calendar/events` | Create calendar event |
| POST | `/api/calendar/sync-deadlines` | Sync project deadlines |

### Email — AgentMail

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/email/agentmail/status` | Connection status |
| GET | `/api/email/agentmail/messages` | List inbox messages |
| POST | `/api/email/agentmail/send` | Send email |

### Email — Gmail

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/email/gmail/messages` | List Gmail messages |
| GET | `/api/email/gmail/thread/{threadId}` | Get thread |
| POST | `/api/email/gmail/send` | Send via Gmail |
| DELETE | `/api/email/gmail/disconnect` | Disconnect OAuth |

### Email — LLM Compose

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/email/compose` | LLM-generated email |

### Dispatch

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/dispatch/execute` | Execute agentic job |
| GET | `/api/dispatch/jobs` | List dispatch jobs |

### GitHub

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/github/sync` | Sync GitHub issues |
| GET | `/api/github/status` | Repo mapping status |

---

## Request/Response Schemas

### POST `/api/email/compose`

**Request:**

```json
{
  "template": "daily-schedule",
  "backend": "ollama",
  "model": "llama3.2",
  "project": "codomyrmex",
  "customPrompt": "Include blockers"
}
```

| Field | Type | Required | Values |
|-------|------|----------|--------|
| template | string | ✅ | `daily-schedule`, `all-projects`, `project-summary`, `interview-followup`, `custom` |
| backend | string | ❌ | `ollama` (default), `claude`, `gemini` |
| model | string | ❌ | LLM model name |
| project | string | ❌ | Project slug (required for `project-summary`) |
| customPrompt | string | ❌ | Used by `custom` template |

**Response (200):**

```json
{
  "success": true,
  "subject": "Daily Schedule — 3/1/2026",
  "body": "1. Today's Calendar...",
  "to": "",
  "template": "daily-schedule",
  "backend": "ollama"
}
```

### POST `/api/projects`

**Request:**

```json
{
  "slug": "my-project",
  "title": "My Project",
  "mission": "Ship it.",
  "status": "active"
}
```

### POST `/api/email/agentmail/send`

**Request:**

```json
{
  "to": "recipient@example.com",
  "subject": "Hello",
  "body": "Message body"
}
```

---

## Error Response

All errors follow:

```json
{
  "success": false,
  "error": "Description of the error"
}
```

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 409 | Conflict |
| 500 | Internal Error |
| 504 | Gateway Timeout |

---

## Timeouts

| Endpoint | Timeout |
|----------|---------|
| `POST /api/email/compose` | 120s |
| `POST /api/dispatch/execute` | 300s |
| All others | 30s |
