"""Offline auth controls and explicitly authorized live calendar lifecycle tests."""

import os
from datetime import UTC, datetime, timedelta

import pytest

from codomyrmex.calendar_integration.mcp_tools import (
    _DEFAULT_ATTENDEE,
    calendar_create_event,
    calendar_delete_event,
    calendar_get_event,
    calendar_list_events,
    calendar_update_event,
)

pytestmark = pytest.mark.integration


@pytest.fixture
def live_calendar() -> None:
    """Require authorization before any token probe, network call or invitation."""
    if os.environ.get("CODOMYRMEX_RUN_LIVE_CALENDAR_TESTS") != "1":
        pytest.skip(
            "Live calendar access requires CODOMYRMEX_RUN_LIVE_CALENDAR_TESTS=1"
        )
    approved_attendee = os.environ.get("CODOMYRMEX_CALENDAR_TEST_ATTENDEE", "")
    if _DEFAULT_ATTENDEE and approved_attendee != _DEFAULT_ATTENDEE:
        pytest.fail(
            "Default calendar attendee requires explicit test-attendee approval"
        )
    result = calendar_list_events(days_ahead=1)
    assert result["status"] == "success", "Live calendar authorization probe failed"


@pytest.mark.network
def test_calendar_mcp_flow(live_calendar):
    """Create/get/update/delete only after live opt-in, always cleaning up."""
    now = datetime.now(UTC)
    created = calendar_create_event(
        summary="Codomyrmex temporary integration event",
        start_time=now.isoformat(),
        end_time=(now + timedelta(hours=1)).isoformat(),
        description="Temporary automated integration control",
        location="Virtual",
        attendees=[],
    )
    assert created["status"] == "success", "Live calendar event creation failed"
    event_id = created["event_id"]
    try:
        fetched = calendar_get_event(event_id)
        assert fetched["status"] == "success", "Live calendar event lookup failed"
        title_matches = (
            fetched["event"]["summary"] == "Codomyrmex temporary integration event"
        )
        assert title_matches, "Created event title did not round-trip"
        updated = calendar_update_event(
            event_id=event_id,
            summary="Codomyrmex updated temporary integration event",
            start_time=now.isoformat(),
            end_time=(now + timedelta(hours=2)).isoformat(),
            description="Temporary automated integration control",
            location="Virtual",
            attendees=[],
        )
        assert updated["status"] == "success", "Live calendar event update failed"
    finally:
        deleted = calendar_delete_event(event_id)
        assert deleted["status"] == "success", "Live calendar cleanup failed"


@pytest.mark.network
def test_calendar_attendee_injection(live_calendar):
    """Invite only the explicitly approved configured test attendee."""
    approved = os.environ.get("CODOMYRMEX_CALENDAR_TEST_ATTENDEE", "")
    if not approved or approved != _DEFAULT_ATTENDEE:
        pytest.skip(
            "Attendee control requires matching explicit test/default attendees"
        )
    now = datetime.now(UTC)
    created = calendar_create_event(
        summary="Codomyrmex temporary attendee integration event",
        start_time=now.isoformat(),
        end_time=(now + timedelta(hours=1)).isoformat(),
        description="Temporary explicitly authorized invitation control",
        attendees=[],
    )
    assert created["status"] == "success", "Live calendar event creation failed"
    event_id = created["event_id"]
    try:
        fetched = calendar_get_event(event_id)
        assert fetched["status"] == "success", "Live calendar event lookup failed"
        attendee_matches = any(
            attendee.lower() == approved.lower()
            for attendee in fetched["event"].get("attendees", [])
        )
        assert attendee_matches, "Approved attendee did not round-trip"
    finally:
        deleted = calendar_delete_event(event_id)
        assert deleted["status"] == "success", "Live calendar cleanup failed"


def test_calendar_error_handling_missing_token():
    """Exercise real auth failure using isolated absent OAuth and ADC files."""
    listed = calendar_list_events()
    assert listed["status"] == "error"
    assert isinstance(listed["message"], str) and listed["message"]
    now = datetime.now(UTC)
    created = calendar_create_event(
        summary="Offline authentication control",
        start_time=now.isoformat(),
        end_time=(now + timedelta(hours=1)).isoformat(),
    )
    assert created["status"] == "error"
    assert isinstance(created["message"], str) and created["message"]
