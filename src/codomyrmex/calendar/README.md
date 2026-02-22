# Codomyrmex Calendar Module

The `calendar` module provides a unified, generic interface for integrating with various calendar providers, with an initial focus on Google Calendar (`gcal`). It adheres strictly to the Codomyrmex Zero-Mock policy, ensuring reliable and verifiable interactions with real calendar APIs.

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
from codomyrmex.calendar import GoogleCalendar, CalendarEvent

# Initialize the provider (requires valid credentials)
provider = GoogleCalendar(credentials=my_google_credentials)

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
- `gcal.py`: The `GoogleCalendar` implementation.

For detailed technical specifications, see [SPEC.md](./SPEC.md). For agent instructions on how to use this module, see [AGENTS.md](./AGENTS.md).
