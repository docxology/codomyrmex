# Personal AI Infrastructure — Calendar Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Calendar module provides calendar event management with provider abstraction. It supports event creation, querying, and management through a generic interface that can be backed by different calendar providers (PAI dashboard, Google Calendar, CalDAV).

## PAI Capabilities

### Event Management

```python
from codomyrmex.calendar import CalendarEvent, CalendarProvider

# Create calendar events
event = CalendarEvent(
    title="Sprint Review",
    start="2026-02-23T10:00:00",
    end="2026-02-23T11:00:00",
    description="Review sprint 25 deliverables"
)

# Use a provider to manage events
provider = CalendarProvider()
provider.create_event(event)
events = provider.list_events(date="2026-02-23")
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `CalendarEvent` | Class | Event data model |
| `CalendarProvider` | Class | Abstract calendar provider interface |
| `cli_commands` | Function | CLI commands for calendar operations |
| Calendar exceptions | Various | `CalendarError`, `EventNotFound`, etc. |

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
