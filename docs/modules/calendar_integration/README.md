# Codomyrmex Calendar Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

The `calendar_integration` module provides a unified, generic interface for integrating with various calendar providers, with an initial focus on Google Calendar (`gcal`). It adheres strictly to the Codomyrmex Zero-Mock policy, ensuring reliable and verifiable interactions with real calendar APIs.

## Features

- **Generic Interface:** Define calendar events and operations using standard Pydantic models and Abstract Base Classes.
- **Google Calendar Integration:** Out-of-the-box support for the Google Calendar API (`v3`).
- **Zero-Mock Testing Compatibility:** Designed to be tested against real APIs using authenticated service accounts or OAuth tokens.

## Installation

Install the module with its optional dependencies:

```bash
uv sync --extra calendar
```

This will install packages such as `google-api-python-client`, `google-auth-httplib2`, and `google-auth-oauthlib`.

## Quick Start

```python
from datetime import datetime, timedelta, timezone
from codomyrmex.calendar_integration import GoogleCalendar, CalendarEvent

# Initialize the provider from environment variables
provider = GoogleCalendar.from_env()

# List events in the next week
now = datetime.now(timezone.utc)
events = provider.list_events(time_min=now, time_max=now + timedelta(days=7))

for event in events:
    print(f"Event: {event.summary} starting at {event.start_time}")

# Create a new event
new_event = CalendarEvent(
    summary="Project Sync",
    description="Weekly sync for the Codomyrmex project.",
    start_time=now + timedelta(days=1),
    end_time=now + timedelta(days=1, hours=1),
    attendees=["user@example.com"]
)
created_event = provider.create_event(new_event)
print(f"Created event ID: {created_event.id}")
```

## Structure

- `exceptions.py`: Custom exceptions for calendar operations.
- `generics.py`: Standard interfaces (`CalendarProvider`, `CalendarEvent`).
- `gcal/provider.py`: The `GoogleCalendar` implementation.
- `mcp_tools.py`: Exposes `GoogleCalendar` operations as MCP Tools (list, create, get, update, delete) for agentic scheduling. Automatically injects `FristonBlanket@gmail.com` (or `CODOMYRMEX_CALENDAR_ATTENDEE` env var) as an attendee on every create/update.

For detailed technical specifications, see [SPEC.md](./SPEC.md). For agent instructions on how to use this module, see [AGENTS.md](./AGENTS.md).

## Authentication Setup

Google Calendar authentication is handled through the PAI dashboard OAuth flow. Follow these steps once:

1. **Start the dashboard** — `uv run python scripts/pai/dashboard.py`
2. **Authenticate** — Follow the OAuth browser prompt that opens. Sign in with the target Google account.
3. **Token saved** — On success, the token is persisted to `~/.codomyrmex/gcal_token.json`. All subsequent MCP tool calls read from this file automatically.

**Required environment variables** (set in `.env` or shell before starting):

| Variable | Where to get it |
|----------|----------------|
| `GOOGLE_CLIENT_ID` | Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | Same credential entry as above |

**Google Cloud Console setup:**
- Enable the **Google Calendar API** for your project.
- Create an OAuth 2.0 credential with application type **Desktop app**.
- Add the scope: `https://www.googleapis.com/auth/calendar`
- Download the client secret JSON and extract `client_id` / `client_secret` into your environment.

## MCP Tools

These tools are auto-discovered and exposed via the Codomyrmex MCP bridge. Agents invoke them without HTTP — the tool handles credential loading internally.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `calendar_list_events` | `days_ahead: int = 7` | List events within the next N days |
| `calendar_create_event` | `summary`, `start_time`, `end_time`, `description`, `location`, `attendees` | Create a new event |
| `calendar_get_event` | `event_id` | Fetch a single event by its Google event ID |
| `calendar_update_event` | `event_id`, `summary`, `start_time`, `end_time`, `description`, `location`, `attendees` | Replace all event fields (PUT semantics — all fields overwritten) |
| `calendar_delete_event` | `event_id` | Permanently delete an event |

**Attendee injection:** `calendar_create_event` and `calendar_update_event` always add `FristonBlanket@gmail.com` (or `CODOMYRMEX_CALENDAR_ATTENDEE` env var) to the attendees list. This cannot be suppressed.

**Datetime format:** All `start_time` / `end_time` parameters must be ISO 8601 strings, e.g. `"2026-02-24T10:00:00Z"` or `"2026-02-24T10:00:00-08:00"`.

## Error Handling

Catch calendar-specific exceptions when using the provider directly:

```python
from codomyrmex.calendar_integration import GoogleCalendar, CalendarEvent
from codomyrmex.calendar_integration.exceptions import (
    CalendarAuthError,
    EventNotFoundError,
    CalendarAPIError,
)

try:
    provider = GoogleCalendar.from_env()
    event = provider.get_event("some_event_id")
except CalendarAuthError as e:
    # Invalid or expired credentials — re-authenticate via PAI dashboard
    print(f"Auth error: {e}")
except EventNotFoundError as e:
    # The event ID does not exist in the calendar
    print(f"Event not found: {e}")
except CalendarAPIError as e:
    # Generic Google Calendar API failure (quota, network, etc.)
    print(f"API error: {e}")
```

**When using MCP tools**, exceptions are caught internally and returned as structured dicts. Always check `result["status"]` before accessing other keys:

```python
result = calendar_get_event("some_event_id")
if result["status"] == "error":
    print(f"Failed: {result['error']}")
else:
    event = result["event"]
```
