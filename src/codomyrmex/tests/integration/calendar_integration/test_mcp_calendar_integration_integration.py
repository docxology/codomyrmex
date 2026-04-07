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

# ---------------------------------------------------------------------------
# Connectivity probe — verify the OAuth credentials actually work, not just
# that the token file exists on disk.  A stale/revoked OAuth client causes
# ``invalid_client`` errors that are not caught by a simple file-exists check.
# ---------------------------------------------------------------------------
_TOKEN_EXISTS = os.path.exists(os.path.expanduser("~/.codomyrmex/gcal_token.json"))
_GCAL_SKIP_REASON = "Requires a valid PAI Google Calendar token"

if _TOKEN_EXISTS:
    _probe = calendar_list_events(days_ahead=1)
    if _probe.get("status") != "success":
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
    """Verify calendar mcp flow behavior."""
    # 1. list
    res = calendar_list_events(days_ahead=2)
    assert res["status"] == "success", f"list events failed: {res}"
    assert "events" in res

    # 2. Create
    now = datetime.now(UTC)
    valid_attendees = [_DEFAULT_ATTENDEE] if _DEFAULT_ATTENDEE else []
    res_create = calendar_create_event(
        summary="Test MCP Agent Event",
        start_time=now.isoformat(),
        end_time=(now + timedelta(hours=1)).isoformat(),
        description="Created via MCP tool",
        location="Virtual",
        attendees=valid_attendees,
    )
    assert res_create["status"] == "success", res_create
    event_id = res_create["event_id"]

    # 3. Get
    res_get = calendar_get_event(event_id)
    assert res_get["status"] == "success"
    assert res_get["event"]["summary"] == "Test MCP Agent Event"

    # 4. Update
    res_update = calendar_update_event(
        event_id=event_id,
        summary="Updated Test MCP Agent Event",
        start_time=now.isoformat(),
        end_time=(now + timedelta(hours=2)).isoformat(),
        description="Updated via MCP tool",
        location="Virtual",
        attendees=valid_attendees,
    )
    assert res_update["status"] == "success", res_update

    # 5. Delete
    res_delete = calendar_delete_event(event_id)
    assert res_delete["status"] == "success"


@pytest.mark.skipif(
    not _GCAL_AVAILABLE,
    reason=_GCAL_SKIP_REASON,
)
def test_calendar_attendee_injection(monkeypatch):
    """Verify that _DEFAULT_ATTENDEE is always injected as an attendee."""
    test_attendee = "test@example.com"
    monkeypatch.setenv("CODOMYRMEX_CALENDAR_ATTENDEE", test_attendee)

    # Needs to match the env var or use monkeypatch's effect on the module.
    # But wait, mcp_tools reads os.environ at IMPORT time!
    # So monkeypatching os.environ during the test execution
    # won't change mcp_tools._DEFAULT_ATTENDEE because it was evaluated at import.
    # We must patch mcp_tools._DEFAULT_ATTENDEE directly!
    import codomyrmex.calendar_integration.mcp_tools as mcp_tools_mod

    monkeypatch.setattr(mcp_tools_mod, "_DEFAULT_ATTENDEE", test_attendee)

    now = datetime.now(UTC)
    res_create = calendar_create_event(
        summary="PAI Attendee Injection Test",
        start_time=now.isoformat(),
        end_time=(now + timedelta(hours=1)).isoformat(),
        description="Automated attendee injection test — safe to delete",
        attendees=[],  # Intentionally empty — injection must still occur
    )
    assert res_create["status"] == "success", f"Create failed: {res_create}"
    event_id = res_create["event_id"]

    try:
        res_get = calendar_get_event(event_id)
        assert res_get["status"] == "success", f"Get failed: {res_get.get('error')}"
        attendees = res_get["event"].get("attendees", [])
        attendees_lower = [a.lower() for a in attendees]
        assert test_attendee.lower() in attendees_lower, (
            f"Expected {test_attendee} in attendees, got: {attendees}"
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
    assert res_list.get("message") or res_list.get("error"), (
        "Expected non-empty error message"
    )

    now = datetime.now(UTC)
    res_create = calendar_create_event(
        summary="Should not be created",
        start_time=now.isoformat(),
        end_time=(now + timedelta(hours=1)).isoformat(),
    )
    assert res_create["status"] == "error", "Expected error status for missing token"
    assert res_create.get("message") or res_create.get("error"), (
        "Expected non-empty error message"
    )
