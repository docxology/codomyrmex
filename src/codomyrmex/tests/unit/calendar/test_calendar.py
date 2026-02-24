"""Unit tests for the calendar module.

Tests CalendarEvent creation and validation, CalendarProvider abstract interface,
CALENDAR_AVAILABLE flag behavior, and exception classes.

Zero-mock policy: no MagicMock or monkeypatch.
Live Google Calendar API tests are guarded by pytest.mark.skipif.
"""

import pytest
from datetime import datetime, timezone, timedelta

import codomyrmex.calendar as cal_module
from codomyrmex.calendar.generics import CalendarEvent, CalendarProvider
from codomyrmex.calendar.exceptions import (
    CalendarError,
    CalendarAuthError,
    CalendarAPIError,
    EventNotFoundError,
    InvalidEventError,
)


# ── CalendarEvent ─────────────────────────────────────────────────────


class TestCalendarEvent:
    """Tests for the CalendarEvent data model."""

    def _event(self, **kwargs) -> CalendarEvent:
        defaults = dict(
            summary="Test Event",
            start_time=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 3, 1, 11, 0, tzinfo=timezone.utc),
        )
        defaults.update(kwargs)
        return CalendarEvent(**defaults)

    def test_minimal_event_creation(self):
        event = self._event()
        assert event.summary == "Test Event"
        assert event.id is None
        assert event.description is None
        assert event.location is None
        assert event.attendees == []
        assert event.html_link is None

    def test_event_with_all_fields(self):
        event = self._event(
            id="evt_123",
            summary="Full Event",
            description="A detailed description",
            location="Conference Room A",
            attendees=["a@example.com", "b@example.com"],
            html_link="https://calendar.google.com/event?eid=123",
        )
        assert event.id == "evt_123"
        assert event.description == "A detailed description"
        assert event.location == "Conference Room A"
        assert len(event.attendees) == 2
        assert "a@example.com" in event.attendees
        assert event.html_link.startswith("https://")

    def test_start_end_times_are_stored(self):
        start = datetime(2026, 3, 1, 9, 0, tzinfo=timezone.utc)
        end = datetime(2026, 3, 1, 10, 30, tzinfo=timezone.utc)
        event = self._event(start_time=start, end_time=end)
        assert event.start_time == start
        assert event.end_time == end

    def test_event_with_timezone_aware_datetimes(self):
        from zoneinfo import ZoneInfo
        tz = ZoneInfo("America/Los_Angeles")
        start = datetime(2026, 3, 1, 10, 0, tzinfo=tz)
        end = datetime(2026, 3, 1, 11, 0, tzinfo=tz)
        event = self._event(start_time=start, end_time=end)
        assert event.start_time.tzinfo is not None
        assert event.end_time.tzinfo is not None

    def test_attendees_default_empty_list(self):
        event = self._event()
        assert isinstance(event.attendees, list)
        assert len(event.attendees) == 0

    def test_summary_is_required(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            CalendarEvent(
                start_time=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
                end_time=datetime(2026, 3, 1, 11, 0, tzinfo=timezone.utc),
            )

    def test_start_time_is_required(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            CalendarEvent(
                summary="Test",
                end_time=datetime(2026, 3, 1, 11, 0, tzinfo=timezone.utc),
            )

    def test_end_time_is_required(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            CalendarEvent(
                summary="Test",
                start_time=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
            )


# ── CalendarProvider ──────────────────────────────────────────────────


class TestCalendarProviderAbstractInterface:
    """Tests that CalendarProvider is abstract and cannot be instantiated directly."""

    def test_cannot_instantiate_abstract_provider(self):
        with pytest.raises(TypeError):
            CalendarProvider()  # type: ignore

    def test_concrete_subclass_must_implement_all_methods(self):
        """A subclass missing any abstract method should also raise TypeError."""

        class IncompleteProvider(CalendarProvider):
            def list_events(self, time_min, time_max):
                return []
            # Missing: create_event, get_event, update_event, delete_event

        with pytest.raises(TypeError):
            IncompleteProvider()  # type: ignore

    def test_complete_subclass_can_be_instantiated(self):
        """A subclass implementing all abstract methods instantiates successfully."""

        class MinimalProvider(CalendarProvider):
            def list_events(self, time_min, time_max):
                return []

            def create_event(self, event):
                return event

            def get_event(self, event_id):
                raise EventNotFoundError(event_id)

            def update_event(self, event_id, event):
                return event

            def delete_event(self, event_id):
                return None

        provider = MinimalProvider()
        assert provider is not None

    def test_complete_provider_list_events_returns_list(self):
        class MinimalProvider(CalendarProvider):
            def list_events(self, time_min, time_max):
                return []

            def create_event(self, event):
                return event

            def get_event(self, event_id):
                raise EventNotFoundError(event_id)

            def update_event(self, event_id, event):
                return event

            def delete_event(self, event_id):
                return None

        provider = MinimalProvider()
        now = datetime.now(timezone.utc)
        result = provider.list_events(now, now + timedelta(days=1))
        assert isinstance(result, list)


# ── CALENDAR_AVAILABLE flag ───────────────────────────────────────────


class TestCalendarAvailabilityFlag:
    """Tests for the CALENDAR_AVAILABLE module-level flag."""

    def test_calendar_available_flag_is_bool(self):
        assert isinstance(cal_module.CALENDAR_AVAILABLE, bool)

    def test_gcal_available_flag_is_bool(self):
        assert isinstance(cal_module.GCAL_AVAILABLE, bool)

    def test_calendar_available_and_gcal_consistent(self):
        # CALENDAR_AVAILABLE is True iff GCAL_AVAILABLE is True
        assert cal_module.CALENDAR_AVAILABLE == cal_module.GCAL_AVAILABLE

    def test_google_calendar_none_when_unavailable(self):
        if not cal_module.CALENDAR_AVAILABLE:
            assert cal_module.GoogleCalendar is None


# ── Exception hierarchy ───────────────────────────────────────────────


class TestCalendarExceptions:
    """Tests for exception classes and hierarchy."""

    def test_calendar_error_is_base(self):
        assert issubclass(CalendarAuthError, CalendarError)
        assert issubclass(CalendarAPIError, CalendarError)
        assert issubclass(EventNotFoundError, CalendarError)
        assert issubclass(InvalidEventError, CalendarError)

    def test_calendar_error_is_exception(self):
        assert issubclass(CalendarError, Exception)

    def test_calendar_auth_error_can_be_raised(self):
        with pytest.raises(CalendarAuthError):
            raise CalendarAuthError("Invalid credentials")

    def test_calendar_api_error_can_be_raised(self):
        with pytest.raises(CalendarAPIError):
            raise CalendarAPIError("API returned 500")

    def test_event_not_found_error_can_be_raised(self):
        with pytest.raises(EventNotFoundError):
            raise EventNotFoundError("event_id_xyz")

    def test_invalid_event_error_can_be_raised(self):
        with pytest.raises(InvalidEventError):
            raise InvalidEventError("Missing timezone info")

    def test_all_exceptions_caught_by_base(self):
        for exc_class in [CalendarAuthError, CalendarAPIError, EventNotFoundError, InvalidEventError]:
            with pytest.raises(CalendarError):
                raise exc_class("test")


# ── Module exports ────────────────────────────────────────────────────


class TestCalendarModuleExports:
    """Tests that the calendar module exports expected symbols."""

    def test_calendar_event_exported(self):
        assert hasattr(cal_module, "CalendarEvent")

    def test_calendar_provider_exported(self):
        assert hasattr(cal_module, "CalendarProvider")

    def test_exceptions_exported(self):
        for name in ["CalendarError", "CalendarAuthError", "CalendarAPIError",
                     "EventNotFoundError", "InvalidEventError"]:
            assert hasattr(cal_module, name), f"Missing export: {name}"

    def test_cli_commands_exported(self):
        assert hasattr(cal_module, "cli_commands")
        commands = cal_module.cli_commands()
        assert isinstance(commands, dict)
        assert "status" in commands


# ── Live Google Calendar tests (skipped unless creds available) ───────


@pytest.mark.skipif(
    not cal_module.CALENDAR_AVAILABLE,
    reason="Google Calendar dependencies not installed (uv sync --extra calendar)"
)
class TestGoogleCalendarLive:
    """Live integration tests — only run when CALENDAR_AVAILABLE is True
    AND gcal_token.json exists. Marked network for CI exclusion."""

    @pytest.mark.network
    def test_google_calendar_provider_is_importable(self):
        from codomyrmex.calendar.gcal.provider import GoogleCalendar
        assert GoogleCalendar is not None
