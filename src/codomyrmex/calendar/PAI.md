# Personal AI Infrastructure — Calendar Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Calendar module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.calendar import CalendarProvider, CalendarEvent, GoogleCalendar
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `CalendarProvider` | Class | Calendarprovider |
| `CalendarEvent` | Class | Calendarevent |
| `GoogleCalendar` | Class | Googlecalendar |
| `CALENDAR_AVAILABLE` | Class | Calendar available |
| `GCAL_AVAILABLE` | Class | Gcal available |
| `CalendarError` | Class | Calendarerror |
| `CalendarAuthError` | Class | Calendarautherror |
| `CalendarAPIError` | Class | Calendarapierror |
| `EventNotFoundError` | Class | Eventnotfounderror |
| `InvalidEventError` | Class | Invalideventerror |

## PAI Algorithm Phase Mapping

| Phase | Calendar Contribution |
|-------|------------------------------|
| **EXECUTE** | General module operations |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
