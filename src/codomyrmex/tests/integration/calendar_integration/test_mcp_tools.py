import os
from datetime import datetime, timedelta, timezone, UTC

import pytest

from codomyrmex.calendar_integration.mcp_tools import (
    _DEFAULT_ATTENDEE,
    calendar_create_event,
    calendar_delete_event,
    calendar_get_event,
    calendar_list_events,
    calendar_update_event,
)

# ---------------------------------------------------------------------------
# Connectivity probe — verify the OAuth credentials actually work, not just
# that the token file exists on disk.  A stale/revoked OAuth client causes
# ``invalid_client`` errors that are not caught by a simple file-exists check.
# ---------------------------------------------------------------------------
_TOKEN_EXISTS = os.path.exists(os.path.expanduser("~/.codomyrmex/gcal_token.json"))
_GCAL_SKIP_REASON = "Requires a valid PAI Google Calendar token"

if _TOKEN_EXISTS:
    _probe = calendar_list_events(days_ahead=1)
    if _probe.get("status") != "ok":
        _GCAL_AVAILABLE = False
        _GCAL_SKIP_REASON = (
            f"GCal token exists but API probe failed: {_probe.get('error', 'unknown')}"
        )
    else:
        _GCAL_AVAILABLE = True
else:
    _GCAL_AVAILABLE = False


@pytest.mark.skipif(
    not _GCAL_AVAILABLE,
    reason=_GCAL_SKIP_REASON,
)
def test_calendar_mcp_flow():
    """Test functionality: calendar mcp flow."""
    # 1. List
    res = calendar_list_events(days_ahead=2)
    assert res["status"] == "ok"
    assert "events" in res

    # 2. Create
    now = datetime.now(UTC)
    res_create = calendar_create_event(
        summary="Test MCP Agent Event",
        start_time=now.isoformat(),
        end_time=(now + timedelta(hours=1)).isoformat(),
        description="Created via MCP tool",
        location="Virtual",
        attendees=[_DEFAULT_ATTENDEE]
    )
    assert res_create["status"] == "ok"
    event_id = res_create["event_id"]

    # 3. Get
    res_get = calendar_get_event(event_id)
    assert res_get["status"] == "ok"
    assert res_get["event"]["summary"] == "Test MCP Agent Event"

    # 4. Update
    res_update = calendar_update_event(
        event_id=event_id,
        summary="Updated Test MCP Agent Event",
        start_time=now.isoformat(),
        end_time=(now + timedelta(hours=2)).isoformat(),
        description="Updated via MCP tool",
        location="Virtual",
        attendees=[_DEFAULT_ATTENDEE]
    )
    assert res_update["status"] == "ok"

    # 5. Delete
    res_delete = calendar_delete_event(event_id)
    assert res_delete["status"] == "ok"


@pytest.mark.skipif(
    not _GCAL_AVAILABLE,
    reason=_GCAL_SKIP_REASON,
)
def test_calendar_attendee_injection():
    """Verify that _DEFAULT_ATTENDEE is always injected as an attendee."""
    now = datetime.now(UTC)
    res_create = calendar_create_event(
        summary="PAI Attendee Injection Test",
        start_time=now.isoformat(),
        end_time=(now + timedelta(hours=1)).isoformat(),
        description="Automated attendee injection test — safe to delete",
        attendees=[],  # Intentionally empty — injection must still occur
    )
    assert res_create["status"] == "ok", f"Create failed: {res_create.get('error')}"
    event_id = res_create["event_id"]

    try:
        res_get = calendar_get_event(event_id)
        assert res_get["status"] == "ok", f"Get failed: {res_get.get('error')}"
        attendees = res_get["event"]["attendees"]
        attendees_lower = [a.lower() for a in attendees]
        assert _DEFAULT_ATTENDEE.lower() in attendees_lower, (
            f"Expected {_DEFAULT_ATTENDEE} in attendees (case-insensitive), got: {attendees}"
        )
    finally:
        calendar_delete_event(event_id)


@pytest.mark.skipif(
    _GCAL_AVAILABLE,  # Inverse — only runs when credentials are NOT working (e.g. CI)
    reason="Skipped when a valid GCal connection exists (tests error path only)",
)
def test_calendar_error_handling_missing_token():
    """Verify MCP tools return error dicts rather than raising when no token exists."""
    res_list = calendar_list_events()
    assert res_list["status"] == "error", "Expected error status for missing token"
    assert res_list.get("error"), "Expected non-empty error message"

    now = datetime.now(UTC)
    res_create = calendar_create_event(
        summary="Should not be created",
        start_time=now.isoformat(),
        end_time=(now + timedelta(hours=1)).isoformat(),
    )
    assert res_create["status"] == "error", "Expected error status for missing token"
    assert res_create.get("error"), "Expected non-empty error message"
