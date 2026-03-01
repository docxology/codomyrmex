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

### 4. Calendar Integration (MCP Tools)

The Google Calendar authentication flow completed within the PAI Dashboard saves an OAuth token to `~/.codomyrmex/gcal_token.json`. Autonomous agents can directly leverage this to manage DanielAriFriedman's schedule by invoking the local Codomyrmex MCP tools (`calendar_list_events`, `calendar_create_event`, etc.).

### 5. Email Integration

The PAI server provides dual email backends:

- **AgentMail** (`/api/email/agentmail/*`): Programmable email for agent-to-agent or agent-to-human messaging.
- **Gmail** (`/api/email/gmail/*`): Authenticated Gmail access (requires OAuth token).

```bash
# Check email connectivity
curl -s http://localhost:8888/api/email/agentmail/status | jq .
curl -s http://localhost:8888/api/email/gmail/messages | jq '.messages | length'

# Send via AgentMail
curl -X POST http://localhost:8888/api/email/agentmail/send \
  -H "Content-Type: application/json" \
  -d '{"to":"recipient@example.com","subject":"Test","body":"Hello from PAI"}'

# Send via Gmail
curl -X POST http://localhost:8888/api/email/gmail/send \
  -H "Content-Type: application/json" \
  -d '{"to":"recipient@example.com","subject":"Test","body":"Hello from PAI"}'
```

### 6. LLM Email Compose

Generate context-driven emails using real project/calendar data and an LLM backend:

```bash
# Daily schedule summary (uses calendar events + active tasks)
curl -X POST http://localhost:8888/api/email/compose \
  -H "Content-Type: application/json" \
  -d '{"template":"daily-schedule","backend":"ollama"}'

# All projects status summary
curl -X POST http://localhost:8888/api/email/compose \
  -H "Content-Type: application/json" \
  -d '{"template":"all-projects","backend":"ollama"}'

# Specific project update
curl -X POST http://localhost:8888/api/email/compose \
  -H "Content-Type: application/json" \
  -d '{"template":"project-summary","backend":"ollama","project":"codomyrmex"}'
```

Available templates: `daily-schedule`, `all-projects`, `project-summary`, `interview-followup`, `custom`.
Available backends: `ollama` (default, local), `claude`, `gemini`.

### 7. Testing Email Compose

```bash
# Full test suite (requires ollama running)
uv run python scripts/pai/test_email_compose.py

# Dry-run: API connectivity only
uv run python scripts/pai/test_email_compose.py --dry-run

# Specific template
uv run python scripts/pai/test_email_compose.py --template daily-schedule
```

## Constraints & Requirements

- Always verify the server is running on `http://localhost:8888` before trying to mutate or query PM state. If not, trigger `scripts/pai/dashboard.py` in the background.
- Respect the Zero-Mock constraint: all HTTP API calls to PAI must be real, interacting with the actual filesystem backing `PMServer.ts`.

---

## Request / Response Schemas

### `POST /api/email/compose`

**Request body:**

```json
{
  "template": "daily-schedule",
  "backend": "ollama",
  "model": "llama3.2",
  "project": "codomyrmex",
  "customPrompt": "Include blockers and risks"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `template` | string | ✅ | `"daily-schedule"` \| `"all-projects"` \| `"project-summary"` \| `"interview-followup"` \| `"custom"` |
| `backend` | string | ❌ | `"ollama"` (default) \| `"claude"` \| `"gemini"` |
| `model` | string | ❌ | LLM model name (default: `"llama3.2"` for ollama) |
| `project` | string | ❌ | Project slug — required for `project-summary`, optional for others |
| `customPrompt` | string | ❌ | Additional instructions — used by `custom` template |

**Response (200):**

```json
{
  "success": true,
  "subject": "Daily Schedule — 2/28/2026",
  "body": "1. Today's Calendar\n- 09:00 AM - PAI Interview...\n2. Active Work\n...",
  "to": "",
  "template": "daily-schedule",
  "backend": "ollama"
}
```

**Context data gathered per template:**

| Template | Missions | Projects | Tasks | Calendar | Custom Prompt |
|----------|----------|----------|-------|----------|---------------|
| `daily-schedule` | Summary | Active only | In-progress + overdue | Today + tomorrow | ❌ |
| `all-projects` | Full | All | Full breakdown by section | Today + tomorrow | ❌ |
| `project-summary` | Summary | Selected | Full breakdown by section | ❌ | ❌ |
| `interview-followup` | Summary | Selected | Summary | ❌ | ❌ |
| `custom` | Full | All | Full breakdown | Today + tomorrow | ✅ |

### `POST /api/projects`

**Request body:**

```json
{
  "slug": "my-project",
  "title": "My Project",
  "mission": "Ship it by Friday.",
  "status": "active",
  "description": "Optional longer description."
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `slug` | string | ✅ | URL-safe identifier, must be unique |
| `title` | string | ✅ | Human-readable display name |
| `mission` | string | ✅ | One-sentence purpose statement |
| `status` | string | ✅ | `"active"` \| `"completed"` \| `"paused"` |
| `description` | string | ❌ | Extended notes |

**Response (200):**

```json
{ "ok": true, "slug": "my-project" }
```

---

### `POST /api/tasks/{project_slug}`

**Request body:**

```json
{
  "text": "Write unit tests for the auth module",
  "priority": "high",
  "section": "Development",
  "assignee": "daniel",
  "blocked_by": []
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `text` | string | ✅ | Task description |
| `priority` | string | ✅ | `"high"` \| `"medium"` \| `"low"` |
| `section` | string | ❌ | Kanban section label |
| `assignee` | string | ❌ | Agent or human identifier |
| `blocked_by` | array | ❌ | List of blocking task IDs |

**Response (200):**

```json
{ "ok": true, "task_id": "t_abc123" }
```

---

## Error Codes Reference

| Code | Meaning | Common Cause |
|------|---------|-------------|
| `200` | OK | Request succeeded |
| `401` | Unauthorized | Missing or invalid auth token |
| `404` | Not Found | Project slug or task ID does not exist |
| `409` | Conflict | Duplicate slug on project creation |
| `500` | Internal Error | PMServer exception — check server logs |

---

## Dispatch Subsystem

The dispatch endpoint runs agentic jobs asynchronously. Select the backend via the `"backend"` field.

| Backend | Value | Notes |
|---------|-------|-------|
| Claude Code | `"claude"` | Invokes `claude -p` subprocess |
| Ollama | `"ollama"` | Local Ollama server must be running |

**Full payload example:**

```json
{
  "action": "task-implement",
  "backend": "claude",
  "context": {
    "project_slug": "my-project",
    "task_id": "t_abc123",
    "instructions": "Implement the feature described in the task."
  }
}
```

**Submit a job:**

```bash
curl -X POST http://localhost:8888/api/dispatch/execute \
  -H "Content-Type: application/json" \
  -d '{"action":"task-implement","backend":"claude","context":{"project_slug":"my-project","task_id":"t_abc123"}}'
```

**Job polling pattern** — poll `GET /api/dispatch/jobs` every 2 seconds; abandon after 60 seconds (30 attempts):

```bash
for i in $(seq 1 30); do
  STATUS=$(curl -s http://localhost:8888/api/dispatch/jobs | jq -r '.jobs[-1].status')
  [ "$STATUS" = "done" ] && break
  sleep 2
done
```

---

## Calendar MCP Tools

These tools are accessible directly from agents without HTTP — they call the Google Calendar API through `~/.codomyrmex/gcal_token.json`. All datetimes must be **ISO 8601** strings (e.g., `"2026-02-24T10:00:00Z"`). `FristonBlanket@gmail.com` is injected automatically as an attendee on every create/update call.

| Tool | Key Parameters | Description |
|------|---------------|-------------|
| `calendar_list_events` | `days_ahead: int = 7` | List upcoming events |
| `calendar_create_event` | `summary`, `start_time`, `end_time`, `description`, `location`, `attendees` | Create a new event |
| `calendar_get_event` | `event_id` | Fetch event details by ID |
| `calendar_update_event` | `event_id`, `summary`, `start_time`, `end_time`, `description`, `location`, `attendees` | Replace event fields (PUT semantics) |
| `calendar_delete_event` | `event_id` | Permanently delete an event |
