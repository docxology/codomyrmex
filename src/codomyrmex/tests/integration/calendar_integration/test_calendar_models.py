"""Tests for the calendar module."""

import os
from datetime import datetime, timedelta, timezone, UTC

import pytest

from codomyrmex.calendar_integration import (
    CALENDAR_AVAILABLE,
    GCAL_AVAILABLE,
    CalendarEvent,
    GoogleCalendar,
)
from codomyrmex.calendar_integration.exceptions import CalendarAuthError

# Require calendar module dependencies
pytestmark = pytest.mark.skipif(
    not CALENDAR_AVAILABLE,
    reason="Calendar module dependencies not installed. Run `uv sync --extra calendar`"
)

def test_calendar_event_model():
    """Test that the generic CalendarEvent model instantiates correctly."""
    now = datetime.now(UTC)
    event = CalendarEvent(
        summary="Test Meeting",
        description="A test description",
        start_time=now,
        end_time=now + timedelta(hours=1),
        location="Virtual",
        attendees=["test@example.com"]
    )

    assert event.summary == "Test Meeting"
    assert event.description == "A test description"
    assert event.location == "Virtual"
    assert len(event.attendees) == 1
    assert event.attendees[0] == "test@example.com"
    assert event.start_time == now


@pytest.mark.skipif(
    not GCAL_AVAILABLE,
    reason="Google Calendar dependencies not installed."
)
def test_google_calendar_auth_error():
    """Test that GoogleCalendar raises CalendarAuthError without credentials."""
    with pytest.raises(CalendarAuthError):
        GoogleCalendar()

# To fully test the Google Calendar integration in a Zero-Mock environment,
# we would need actual valid credentials. The following test is skipped by
# default unless a specific environment variable is present indicating that
# it's safe to run the integration tests against a real account.
@pytest.mark.skipif(
    os.environ.get("CODOMYRMEX_RUN_LIVE_CALENDAR_TESTS") != "1",
    reason="Live calendar tests require CODOMYRMEX_RUN_LIVE_CALENDAR_TESTS=1 and credentials."
)
def test_google_calendar_live_integration():
    """
    Live integration test for Google Calendar.
    Requires CODOMYRMEX_RUN_LIVE_CALENDAR_TESTS=1 and local credentials setups
    such as ADC (Application Default Credentials) being present.
    """
    try:
        from google.auth import default
        creds, _ = default()
    except Exception as e:
        pytest.skip(f"Could not load default Google credentials: {e}")

    provider = GoogleCalendar(credentials=creds)

    # 1. List events (make sure it doesn't crash)
    now = datetime.now(UTC)
    events = provider.list_events(now, now + timedelta(days=7))
    assert isinstance(events, list)

    # We could theoretically create an event, assert it's returned by get_event,
    # and then delete it. However, we'll keep this simple for safety unless more
    # explicit setup/teardown is implemented.
    pass
