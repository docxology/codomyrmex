# Codomyrmex Agents -- src/codomyrmex/calendar_integration/gcal

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides the `GoogleCalendar` class implementing the `CalendarProvider` interface for Google Calendar API operations. Handles CRUD operations on calendar events, serialization between Google API DTOs and internal `CalendarEvent` models, and multiple credential acquisition strategies.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `provider.py` | `GoogleCalendar` | Concrete `CalendarProvider` implementation for Google Calendar API v3 |
| `provider.py` | `GoogleCalendar.from_env()` | Factory classmethod to create instances from environment variables or token files |

## Operating Contracts

- `GoogleCalendar.__init__()` requires either `credentials` or a pre-built `service` object; raises `CalendarAuthError` if neither is provided, `ImportError` if Google API libraries are missing.
- `from_env()` tries three credential sources in order: env vars (`GOOGLE_REFRESH_TOKEN` + `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`), token file (`~/.codomyrmex/gcal_token.json`), Application Default Credentials.
- All CRUD methods raise `CalendarAPIError` for API failures and `EventNotFoundError` (HTTP 404) for missing events.
- `_gcal_dict_to_event()` raises `InvalidEventError` if response dicts have missing or unparseable datetime fields.
- `list_events()` returns up to 2500 events sorted by start time.
- UTC `Z` suffix is normalized to `+00:00` for Python `datetime.fromisoformat()` compatibility.

## Agent Testing Notes

- This module connects directly to the authenticated Google Calendar API.
- Under zero-mock policy, API calls must never be intercepted with fake responses.
- Tests requiring credentials should use `@pytest.mark.skipif` when env vars are absent.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `calendar_integration.generics` (CalendarProvider, CalendarEvent), `calendar_integration.exceptions` (CalendarAPIError, CalendarAuthError, EventNotFoundError, InvalidEventError), `google-api-python-client`, `google-auth` (optional)
- **Used by**: `calendar_integration.mcp_tools`, any consumer of calendar functionality

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../README.md](../../../README.md)
