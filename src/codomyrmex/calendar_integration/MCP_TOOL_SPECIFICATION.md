# Calendar Module — MCP Tool Specification

This document describes the 5 MCP tools exposed by `codomyrmex.calendar.mcp_tools`.

All tools require:
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` environment variables
- `~/.codomyrmex/gcal_token.json` (written by PAI dashboard OAuth flow)
- Google Calendar dependencies installed: `uv sync --extra calendar`

---

## `calendar_list_events`

List upcoming events from Google Calendar.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `days_ahead` | `int` | No | Number of days to look ahead (default 7) |

### Output Schema

```json
{
  "status": "ok",
  "events": [
    {
      "id": "abc123_20260224T100000Z",
      "summary": "Team Meeting",
      "start_time": "2026-02-24T10:00:00+00:00",
      "end_time": "2026-02-24T11:00:00+00:00",
      "description": "Weekly sync",
      "location": "Zoom",
      "attendees": ["colleague@example.com"],
      "html_link": "https://www.google.com/calendar/event?eid=..."
    }
  ]
}
```

On error: `{"status": "error", "error": "<message>"}`

---

## `calendar_create_event`

Create a new event in Google Calendar.

> **Note**: `danielarifriedman@gmail.com` is automatically added to `attendees` on every event, even when `attendees=[]` or `attendees=None`.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `summary` | `str` | Yes | Event title |
| `start_time` | `str` | Yes | ISO 8601 string, e.g. `"2026-02-24T10:00:00Z"` |
| `end_time` | `str` | Yes | ISO 8601 string, e.g. `"2026-02-24T11:00:00Z"` |
| `description` | `str` | No | Event description (default empty) |
| `location` | `str` | No | Location (default empty) |
| `attendees` | `List[str] \| None` | No | Additional attendee email addresses |

### Output Schema

```json
{
  "status": "ok",
  "event_id": "abc123_20260224T100000Z",
  "link": "https://www.google.com/calendar/event?eid=..."
}
```

On error: `{"status": "error", "error": "<message>"}`

---

## `calendar_get_event`

Get details of a specific calendar event by its provider ID.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_id` | `str` | Yes | Google Calendar event ID |

### Output Schema

```json
{
  "status": "ok",
  "event": {
    "id": "abc123_20260224T100000Z",
    "summary": "Team Meeting",
    "start_time": "2026-02-24T10:00:00+00:00",
    "end_time": "2026-02-24T11:00:00+00:00",
    "description": "Weekly sync",
    "location": "Zoom",
    "attendees": ["colleague@example.com"],
    "html_link": "https://www.google.com/calendar/event?eid=..."
  }
}
```

On error: `{"status": "error", "error": "<message>"}`

---

## `calendar_delete_event`

Permanently delete a calendar event by ID.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_id` | `str` | Yes | Google Calendar event ID to delete |

### Output Schema

```json
{
  "status": "ok",
  "deleted": true
}
```

On error: `{"status": "error", "error": "<message>"}`

---

## `calendar_update_event`

Update an existing calendar event (PUT semantics — all fields replaced).

> **Note**: `danielarifriedman@gmail.com` is automatically added to `attendees` on every update.

### Input Schema

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `event_id` | `str` | Yes | Google Calendar event ID to update |
| `summary` | `str` | Yes | Replacement event title |
| `start_time` | `str` | Yes | ISO 8601 string, e.g. `"2026-02-24T10:00:00Z"` |
| `end_time` | `str` | Yes | ISO 8601 string, e.g. `"2026-02-24T11:00:00Z"` |
| `description` | `str` | No | Replacement description (default empty) |
| `location` | `str` | No | Replacement location (default empty) |
| `attendees` | `List[str] \| None` | No | Replacement attendee list |

### Output Schema

```json
{
  "status": "ok",
  "event_id": "abc123_20260224T100000Z",
  "link": "https://www.google.com/calendar/event?eid=..."
}
```

On error: `{"status": "error", "error": "<message>"}`
