# Google Calendar -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements the `CalendarProvider` interface for Google Calendar API v3. Provides a translation layer between Google API DTOs and the system's `CalendarEvent` model, with support for timed events, all-day events, and attendee management.

## Architecture

Adapter pattern: `GoogleCalendar` wraps the `google-api-python-client` service object and translates between Google Calendar JSON structures and internal `CalendarEvent` dataclasses. Multiple credential acquisition strategies are supported via the `from_env()` factory.

## Key Classes

### `GoogleCalendar`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `credentials: Credentials or None, service: Resource or None` | -- | Initialize with Google credentials or pre-built service |
| `from_env` | *(classmethod)* | `GoogleCalendar` | Create from env vars, token file, or ADC |
| `list_events` | `time_min: datetime, time_max: datetime, calendar_id: str` | `list[CalendarEvent]` | List events in a time range (max 2500) |
| `create_event` | `event: CalendarEvent, calendar_id: str` | `CalendarEvent` | Create a new event |
| `get_event` | `event_id: str, calendar_id: str` | `CalendarEvent` | Fetch a specific event by ID |
| `update_event` | `event_id: str, event: CalendarEvent, calendar_id: str` | `CalendarEvent` | Update an existing event |
| `delete_event` | `event_id: str, calendar_id: str` | `None` | Delete an event |

### Internal Serialization

| Method | Description |
|--------|-------------|
| `_event_to_gcal_dict` | Serialize `CalendarEvent` to Google API request body; omits `None` optional fields |
| `_gcal_dict_to_event` | Deserialize Google API response to `CalendarEvent`; handles `dateTime` and `date` formats |

### Credential Acquisition (`from_env`)

Tries sources in order:
1. Environment variables: `GOOGLE_REFRESH_TOKEN` + `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`
2. Token file: `~/.codomyrmex/gcal_token.json` (requires `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`)
3. Application Default Credentials (`google.auth.default`)

## Dependencies

- **Internal**: `calendar_integration.generics` (CalendarProvider, CalendarEvent), `calendar_integration.exceptions`
- **External**: `google-api-python-client`, `google-auth` (optional; install via `uv sync --extra calendar`)

## Constraints

- `dateTime` strings with `Z` suffix are normalized to `+00:00` for `datetime.fromisoformat()` compatibility.
- All-day events use `date` field instead of `dateTime`; resulting `CalendarEvent.start_time` will lack timezone info.
- Optional fields (`description`, `location`, `attendees`) are omitted from API requests when `None` or empty.
- Zero-mock: real API calls only, `ImportError` when Google libraries are missing.

## Error Handling

- `ImportError`: raised if `google-api-python-client` or `google-auth` are not installed.
- `CalendarAuthError`: raised when no valid credentials can be obtained.
- `CalendarAPIError`: raised for Google Calendar API errors (wraps `HttpError`).
- `EventNotFoundError`: raised for HTTP 404 responses on get/update/delete.
- `InvalidEventError`: raised when API response dicts have unparseable fields.
