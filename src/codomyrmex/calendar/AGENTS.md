# Agent Instructions for `codomyrmex.calendar`

## Context

The `calendar` module provides the Codomyrmex ecosystem with a unified, standard interface to interact with third-party calendar providers. It currently features Google Calendar support.

## Usage Guidelines

1. **Importing:** Always import `CalendarProvider`, `CalendarEvent`, and exceptions directly from the `calendar` module root.

   ```python
   from codomyrmex.calendar import CalendarEvent, CalendarError, GoogleCalendar
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

5. **Error Handling:**
   Catch specific exceptions such as `EventNotFoundError` and `CalendarAuthError` dynamically, logging them descriptively with the `AgentEventBus` or standard python `logging`. Do not use generic block catch-alls like `except Exception: pass` when dealing with the calendar.
