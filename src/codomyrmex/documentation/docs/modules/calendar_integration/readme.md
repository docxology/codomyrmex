# Calendar Integration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Calendar Integration module provides generic calendar interfaces and a Google Calendar provider for event management within the codomyrmex platform. It defines an abstract `CalendarProvider` and `CalendarEvent` model, with a concrete `GoogleCalendar` implementation. This is an optional module requiring `uv sync --extra calendar` for Google Calendar dependencies.

## Architecture Overview

```
calendar_integration/
├── __init__.py              # Public API with conditional imports
├── exceptions.py            # CalendarError hierarchy (5 types)
├── mcp_tools.py             # MCP tools (5 calendar_* tools)
├── generics.py              # CalendarEvent model, CalendarProvider interface
└── gcal/                    # Google Calendar provider implementation
```

## Key Classes and Functions

**`CalendarProvider`** -- Abstract interface for calendar backends.

**`CalendarEvent`** -- Data model for calendar events (title, start, end, description, attendees).

**`GoogleCalendar`** -- Google Calendar API implementation of CalendarProvider.

## MCP Tools Reference

| Tool | Description | Parameters | Trust Level |
|------|-------------|------------|-------------|
| `calendar_list_events` | List calendar events within a date range | `start: str`, `end: str` | Safe |
| `calendar_create_event` | Create a new calendar event | `title: str`, `start: str`, `end: str`, `description: str` | Safe |
| `calendar_get_event` | Get details of a specific event | `event_id: str` | Safe |
| `calendar_delete_event` | Delete a calendar event | `event_id: str` | Safe |
| `calendar_update_event` | Update an existing calendar event | `event_id: str`, `updates: dict` | Safe |

## Configuration

```bash
uv sync --extra calendar    # Install Google Calendar dependencies
export GOOGLE_CALENDAR_CREDENTIALS="path/to/credentials.json"
```

## Error Handling

- `CalendarError` -- Base exception
- `CalendarAuthError` -- Authentication failures
- `CalendarAPIError` -- API communication errors
- `EventNotFoundError` -- Event not found
- `InvalidEventError` -- Invalid event data

## Related Modules

- [`email`](../email/readme.md) -- Email integration for event notifications
- [`collaboration`](../collaboration/readme.md) -- Multi-agent scheduling

## Navigation

- **Source**: [src/codomyrmex/calendar_integration/](../../../../src/codomyrmex/calendar_integration/)
- **Parent**: [All Modules](../README.md)
