# Calendar Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `calendar` module provides a provider-agnostic interface for reading and managing calendar events. It ships with `GoogleCalendar` as the concrete provider implementing the abstract `CalendarProvider` interface. All datetime fields must be timezone-aware.

Install calendar dependencies:
```bash
uv sync --extra calendar
```

## 2. Core Components

### 2.1 Data Models (`generics.py`)

**`CalendarEvent`** (`pydantic.BaseModel`): A calendar event.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str \| None` | No | Provider-assigned event ID; `None` for unsaved events |
| `summary` | `str` | Yes | Event title shown in calendar UIs |
| `description` | `str \| None` | No | Free-text body or agenda |
| `start_time` | `datetime` | Yes | Timezone-aware start datetime |
| `end_time` | `datetime` | Yes | Timezone-aware end datetime |
| `location` | `str \| None` | No | Physical or virtual location |
| `attendees` | `List[str]` | No | Attendee email addresses |
| `html_link` | `str \| None` | No | URL to open event in browser (provider-assigned) |

> **Important**: `start_time` and `end_time` must be timezone-aware. Pass naive datetimes through `dt.replace(tzinfo=timezone.utc)` or use `zoneinfo.ZoneInfo`. Providers may raise `InvalidEventError` for timezone-naive values.

### 2.2 Abstract Provider (`generics.py`)

**`CalendarProvider`** (abstract base class) — all concrete providers implement this interface:

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `list_events` | `(time_min: datetime, time_max: datetime)` | `List[CalendarEvent]` | List events in a time window, ordered by start time |
| `create_event` | `(event: CalendarEvent)` | `CalendarEvent` | Create event; returns saved version with provider ID |
| `get_event` | `(event_id: str)` | `CalendarEvent` | Fetch a single event by provider ID |
| `update_event` | `(event_id: str, event: CalendarEvent)` | `CalendarEvent` | Replace all event fields (PUT semantics) |
| `delete_event` | `(event_id: str)` | `None` | Permanently delete an event |

### 2.3 Concrete Provider

- **`GoogleCalendar`**: Implements `CalendarProvider` via the Google Calendar API v3. Initialized with `google.oauth2.credentials.Credentials`. The `credentials` argument is required.

### 2.4 Exception Hierarchy (`exceptions.py`)

```
CalendarError (base)
├── CalendarAuthError   — authentication with provider failed / credentials expired
├── CalendarAPIError    — provider API returned an unexpected error
├── EventNotFoundError  — requested event ID does not exist
└── InvalidEventError   — event data invalid (e.g. timezone-naive datetime)
```

### 2.5 Availability Flag (`__init__.py`)

| Flag | Type | Description |
|------|------|-------------|
| `CALENDAR_AVAILABLE` | `bool` | True if Google Calendar dependencies are installed |

## 3. Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_CLIENT_ID` | Yes (for OAuth) | Google OAuth2 client ID |
| `GOOGLE_CLIENT_SECRET` | Yes (for OAuth) | Google OAuth2 client secret |

Token storage: `~/.codomyrmex/gcal_token.json` (written by PAI dashboard OAuth flow).

## 4. Usage Example

```python
from datetime import datetime, timezone
from codomyrmex.calendar import CalendarProvider, CalendarEvent, CALENDAR_AVAILABLE

if CALENDAR_AVAILABLE:
    from codomyrmex.calendar.gcal.provider import GoogleCalendar
    from google.oauth2.credentials import Credentials

    creds = Credentials(token="...", refresh_token="...",
                        token_uri="https://oauth2.googleapis.com/token",
                        client_id="...", client_secret="...")
    cal: CalendarProvider = GoogleCalendar(credentials=creds)

    # List next 7 days of events
    now = datetime.now(timezone.utc)
    from datetime import timedelta
    events = cal.list_events(time_min=now, time_max=now + timedelta(days=7))
    for event in events:
        print(f"{event.summary}: {event.start_time.isoformat()}")

    # Create an event
    new_event = CalendarEvent(
        summary="Team Meeting",
        start_time=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 3, 1, 11, 0, tzinfo=timezone.utc),
        attendees=["colleague@example.com"]
    )
    created = cal.create_event(new_event)
    print(f"Created: {created.id} — {created.html_link}")
```
