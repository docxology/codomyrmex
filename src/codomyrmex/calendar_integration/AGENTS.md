# Agent Instructions for `codomyrmex.calendar_integration`

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Unified calendar integration for the Codomyrmex platform, currently featuring Google Calendar
support. Provides `GoogleCalendar` for event CRUD operations, `CalendarEvent` for typed event
data, and five MCP tools for agent-driven scheduling. All events must use timezone-aware
`datetime` objects. Requires `uv sync --extra calendar` and a valid `gcal_token.json`.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `CalendarProvider`, `CalendarEvent`, `GoogleCalendar`, `GCAL_AVAILABLE`, exceptions |
| `google/provider.py` | `GoogleCalendar` — Google Calendar OAuth2 provider implementation |
| `generics.py` | `CalendarProvider` ABC, `CalendarEvent` Pydantic model, `CalendarAddress` |
| `exceptions.py` | `CalendarAuthError`, `EventNotFoundError`, `CalendarError` |
| `mcp_tools.py` | MCP tools: `calendar_list_events`, `calendar_create_event`, `calendar_get_event`, `calendar_delete_event`, `calendar_update_event` |

## Key Classes

- **`GoogleCalendar`** — Google Calendar provider with OAuth2 via `gcal_token.json`
- **`CalendarProvider`** — Abstract base class all providers must implement
- **`CalendarEvent`** — Pydantic model for calendar events (start, end, title, attendees, etc.)
- **`GCAL_AVAILABLE`** — Boolean flag indicating whether Google Calendar SDK is installed

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `calendar_list_events` | List calendar events for a given time range | SAFE |
| `calendar_create_event` | Create a new calendar event | SAFE |
| `calendar_get_event` | Fetch a specific calendar event by ID | SAFE |
| `calendar_delete_event` | Delete a calendar event by ID | TRUSTED |
| `calendar_update_event` | Update an existing calendar event | SAFE |

## Agent Instructions

1. **Check availability first** — Check `GCAL_AVAILABLE` before any Google Calendar code; if `False`, instruct user to `uv sync --extra calendar`
2. **Always use timezone-aware datetimes** — Replace naive datetimes via `datetime.replace(tzinfo=timezone.utc)` or `ZoneInfo` before passing to `CalendarEvent`
3. **Use MCP tools for scheduling** — Prefer `calendar_create_event` MCP tool over direct `GoogleCalendar.create_event()` for autonomous agent use
4. **Catch specific exceptions** — Catch `EventNotFoundError` and `CalendarAuthError`; never use bare `except Exception: pass`
5. **Zero-Mock Policy** — Tests must never mock Google Calendar API calls; use `pytest.mark.skipif` when credentials are unavailable

## Operating Contracts

- **Attendee injection**: `calendar_create_event` and `calendar_update_event` unconditionally add `FristonBlanket@gmail.com` to attendees. This behavior **cannot be suppressed** without modifying `mcp_tools.py`. Override the default address via `CODOMYRMEX_CALENDAR_ATTENDEE` env var
- **Bidirectional sync**: The PAI dashboard (`:8888`) and MCP tools read from the same `~/.codomyrmex/gcal_token.json` — no separate sync job needed; events created via either path appear in the same Google Calendar
- **Timezone requirement**: All `datetime` objects in `CalendarEvent` must be timezone-aware — naive datetimes raise `ValueError`
- **Token file path**: Auth reads from `~/.codomyrmex/gcal_token.json` — ensure this file exists and is valid before calling any event operation

## Common Patterns

```python
from codomyrmex.calendar_integration import CalendarEvent, GCAL_AVAILABLE, GoogleCalendar
from datetime import datetime
from zoneinfo import ZoneInfo

if not GCAL_AVAILABLE:
    raise ImportError("Run: uv sync --extra calendar")

# Create an event with named timezone
tz = ZoneInfo("America/Los_Angeles")
event = CalendarEvent(
    title="Sprint Review",
    start=datetime(2026, 3, 15, 10, 0, 0, tzinfo=tz),
    end=datetime(2026, 3, 15, 11, 0, 0, tzinfo=tz),
)
cal = GoogleCalendar()
created = cal.create_event(event)

# ISO 8601 strings also accepted by MCP tools:
# "2026-03-15T18:00:00Z"        ← UTC
# "2026-03-15T10:00:00-08:00"   ← Offset notation
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `calendar_list_events`, `calendar_create_event`, `calendar_get_event`, `calendar_delete_event`, `calendar_update_event` | TRUSTED |
| **Architect** | Read + Design | `calendar_list_events`, `calendar_get_event` — schema review, scheduling design | OBSERVED |
| **QATester** | Validation | `calendar_list_events`, `calendar_get_event` — event correctness, scheduling verification | OBSERVED |
| **Researcher** | Read-only | `calendar_list_events`, `calendar_get_event` — inspect calendar state for analysis | SAFE |

### Engineer Agent
**Use Cases**: Creating and managing calendar events during EXECUTE, scheduling automated tasks, tracking project milestones.

### Architect Agent
**Use Cases**: Reviewing calendar integration design, planning scheduling architecture, analyzing event data models.

### QATester Agent
**Use Cases**: Verifying calendar events were created correctly, confirming scheduling logic during VERIFY.

### Researcher Agent
**Use Cases**: Inspecting calendar events and schedules for research analysis and planning insights.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
