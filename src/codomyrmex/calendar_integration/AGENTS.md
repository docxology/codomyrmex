# Agent Instructions for `codomyrmex.calendar_integration`

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Context

The `calendar_integration` module provides the Codomyrmex ecosystem with a unified, standard interface to interact with third-party calendar providers. It currently features Google Calendar support.

## Usage Guidelines

1. **Importing:** Always import `CalendarProvider`, `CalendarEvent`, and exceptions directly from the `calendar_integration` module root.

   ```python
   from codomyrmex.calendar_integration import CalendarEvent, CalendarError, GoogleCalendar
   ```

2. **Availability Check:**
   Before running any Google Calendar code, check the `GCAL_AVAILABLE` flag, and instruct the user to install the dependencies if it evaluates to `False`.

   ```bash
   uv sync --extra calendar
   ```

3. **Zero-Mock Policy:**
   When writing tests involving the calendar module, **never mock** the `GoogleCalendar` API interactions. Rely strictly on authentic responses. Use `pytest.mark.skipif` to bypass tests if valid credentials are not accessible in the test environment (e.g., if a `pytest.fixture` fails to find required environment variables).

4. **Timezones:**
   Ensure all `datetime` objects interacting with `CalendarEvent` are timezone-aware.
   Replace naive datetimes via `datetime.replace(tzinfo=timezone.utc)` or similar before attempting to map to physical objects.

   **Example — attaching timezone info before passing to `CalendarEvent`:**
   ```python
   from datetime import datetime
   from zoneinfo import ZoneInfo

   # Option A: Use zoneinfo for named timezones (Python 3.9+)
   tz_la = ZoneInfo("America/Los_Angeles")
   start = datetime(2026, 3, 1, 10, 0, 0, tzinfo=tz_la)

   # Option B: UTC via timezone.utc (always safe)
   from datetime import timezone
   start_utc = datetime(2026, 3, 1, 18, 0, 0, tzinfo=timezone.utc)

   # Equivalent ISO 8601 string formats accepted by mcp_tools:
   # "2026-03-01T18:00:00Z"        ← UTC, Z suffix
   # "2026-03-01T10:00:00-08:00"   ← Named offset
   ```

5. **Error Handling:**
   Catch specific exceptions such as `EventNotFoundError` and `CalendarAuthError` dynamically, logging them descriptively with the `AgentEventBus` or standard python `logging`. Do not use generic block catch-alls like `except Exception: pass` when dealing with the calendar.

6. **Agentic Scheduling (MCP Tools):**
   When autonomous agents interact with the Codomyrmex backend to manage Daniel's tasks, they should leverage the integrated MCP tools (`calendar_create_event`, `calendar_list_events`, `calendar_update_event`, `calendar_delete_event`). These tools gracefully handle initialization via `.codomyrmex/gcal_token.json`.

   **Bidirectional Sync:** Both the PMServer.ts PAI dashboard (`:8888`) and the Codomyrmex MCP tools read from the same `~/.codomyrmex/gcal_token.json` OAuth token file, which authenticates against the same Google account. This means there is no separate sync job — any event created via either path appears in the same Google Calendar, and reads from either path reflect the same ground truth. No additional polling or reconciliation is needed.

   **Attendee Injection Behavior:** Every call to `calendar_create_event` or `calendar_update_event` unconditionally adds `FristonBlanket@gmail.com` to the attendees list before sending the request to Google Calendar. This behavior is triggered regardless of what the caller passes in the `attendees` parameter:
   - If `attendees=None` → list is initialized to `["FristonBlanket@gmail.com"]`
   - If `attendees=[...]` and the address is absent → it is appended
   - If `attendees=[..., "FristonBlanket@gmail.com"]` → no duplicate is added

   This injection **cannot be suppressed** without modifying `mcp_tools.py` directly. It guarantees Daniel always appears as an attendee on every calendar event managed through this system. The default attendee address can be overridden at runtime via the `CODOMYRMEX_CALENDAR_ATTENDEE` environment variable.
