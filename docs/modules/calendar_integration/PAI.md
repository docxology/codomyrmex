# Personal AI Infrastructure — Calendar Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Calendar module provides calendar event management with provider abstraction. It supports event creation, querying, and management through a generic interface that can be backed by different calendar providers (PAI dashboard, Google Calendar, CalDAV).

## PAI Capabilities

### Event Management

```python
from datetime import datetime, timedelta, timezone
from codomyrmex.calendar_integration import CalendarEvent, GoogleCalendar

# Initialize the provider from environment variables
provider = GoogleCalendar.from_env()

# Create a calendar event
event = CalendarEvent(
    summary="Sprint Review",
    start_time=datetime(2026, 2, 23, 10, 0, tzinfo=timezone.utc),
    end_time=datetime(2026, 2, 23, 11, 0, tzinfo=timezone.utc),
    description="Review sprint 25 deliverables"
)

created = provider.create_event(event)
now = datetime.now(timezone.utc)
events = provider.list_events(time_min=now, time_max=now + timedelta(days=7))
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `CalendarEvent` | Class | Event data model |
| `CalendarProvider` | Class | Abstract calendar provider interface |
| `GoogleCalendar` | Class | Google Calendar implementation |
| `CALENDAR_AVAILABLE` | Constant | Whether Google Calendar dependencies are installed |
| Calendar exceptions | Various | `CalendarError`, `CalendarAuthError`, `CalendarAPIError`, `EventNotFoundError`, `InvalidEventError` |

## PAI Algorithm Phase Mapping

| Phase | Calendar Contribution |
|-------|------------------------|
| **OBSERVE** | Query upcoming events and deadlines for context |
| **PLAN** | Schedule tasks and milestones on the calendar |
| **EXECUTE** | Create events for completed work items |

## Architecture Role

**Extended Layer** — Integrated with PAI dashboard for visual calendar management. Consumed by `logistics/` for scheduling.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
