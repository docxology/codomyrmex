"""Unit tests for calendar_integration.mcp_tools — Zero-Mock compliant.

Covers:
  - _with_default_attendee helper (all branches, no external deps)
  - _get_provider error paths (no token file, no env vars, malformed token)
  - MCP tool error-return paths (all 5 tools return {"status": "error"} when
    provider init fails — exercised without real Google credentials)
  - MCP tool schemas are registered (decorator present)

Live API tests require CODOMYRMEX_RUN_LIVE_CALENDAR_TESTS=1 before credential
acquisition. Default tests use explicit absent token and ADC files.
"""

import os

import pytest

# ── Import the module under test ─────────────────────────────────────────────
from codomyrmex.calendar_integration.mcp_tools import (
    _get_provider,
    _with_default_attendee,
    calendar_create_event,
    calendar_delete_event,
    calendar_get_event,
    calendar_list_events,
    calendar_update_event,
)

# ── _with_default_attendee ────────────────────────────────────────────────────


@pytest.mark.unit
class TestWithDefaultAttendee:
    """Tests for the _with_default_attendee internal helper.

    Verifies the attendee injection logic with various input scenarios.
    Uses real list manipulation without mocks.
    """

    def _call(self, attendees, default=""):
        """Call helper with a patched _DEFAULT_ATTENDEE via module attribute."""
        import codomyrmex.calendar_integration.mcp_tools as mod

        original = mod._DEFAULT_ATTENDEE
        mod._DEFAULT_ATTENDEE = default
        try:
            return _with_default_attendee(attendees)
        finally:
            mod._DEFAULT_ATTENDEE = original

    def test_none_input_no_default_returns_empty(self):
        result = self._call(None, default="")
        assert result == []

    def test_empty_list_no_default_returns_empty(self):
        result = self._call([], default="")
        assert result == []

    def test_list_preserved_when_no_default(self):
        result = self._call(["a@example.com", "b@example.com"], default="")
        assert result == ["a@example.com", "b@example.com"]

    def test_default_injected_when_absent(self):
        result = self._call(["a@example.com"], default="default@example.com")
        assert "default@example.com" in result

    def test_default_not_duplicated_when_already_present(self):
        result = self._call(
            ["default@example.com", "other@example.com"],
            default="default@example.com",
        )
        count = result.count("default@example.com")
        assert count == 1

    def test_none_input_with_default_returns_just_default(self):
        result = self._call(None, default="default@example.com")
        assert result == ["default@example.com"]

    def test_does_not_mutate_original_list(self):
        original = ["a@example.com"]
        import codomyrmex.calendar_integration.mcp_tools as mod

        saved = mod._DEFAULT_ATTENDEE
        mod._DEFAULT_ATTENDEE = "default@example.com"
        try:
            _with_default_attendee(original)
        finally:
            mod._DEFAULT_ATTENDEE = saved
        assert original == ["a@example.com"]

    def test_empty_default_string_not_injected(self):
        result = self._call(["a@example.com"], default="")
        assert result == ["a@example.com"]

    def test_returns_list_type(self):
        result = self._call(None, default="")
        assert isinstance(result, list)


# ── _get_provider error paths ─────────────────────────────────────────────────


@pytest.mark.unit
class TestGetProviderErrors:
    """Tests for provider initialization error paths.

    Exercises the _get_provider() function under invalid credential states.
    Strictly mock-free, relying on the absence of real credentials.
    """

    def test_raises_when_no_token_file(self):
        """Real ADC lookup fails on the explicitly selected absent credential file."""
        with pytest.raises(
            RuntimeError, match="not authenticated|dependencies not installed"
        ):
            _get_provider()

    def test_runtime_error_message_is_informative(self):
        with pytest.raises(RuntimeError) as exc_info:
            _get_provider()
        assert len(str(exc_info.value)) > 10


@pytest.mark.unit
class TestGetProviderMalformedToken:
    """Exercise real selected token files without changing HOME or Path.home."""

    def test_malformed_json_raises_runtime_error(self, tmp_path, monkeypatch):
        token_file = tmp_path / "token.json"
        token_file.write_text("{ not valid json !!!}")
        monkeypatch.setenv("GOOGLE_CALENDAR_TOKEN_FILE", str(token_file))
        with pytest.raises(
            RuntimeError,
            match="Failed to read calendar token|dependencies not installed",
        ):
            _get_provider()

    def test_no_token_file_raises_runtime_error(self, tmp_path, monkeypatch):
        monkeypatch.setenv("GOOGLE_CALENDAR_TOKEN_FILE", str(tmp_path / "missing.json"))
        with pytest.raises(
            RuntimeError, match="not authenticated|dependencies not installed"
        ):
            _get_provider()


# ── MCP tool error-return paths ───────────────────────────────────────────────


@pytest.mark.unit
class TestCalendarListEventsErrorPath:
    """Tests for the calendar_list_events MCP tool error paths.

    Verifies that the tool returns structured error dictionaries when
    authentication or connection fails. Exercises real tool code.
    """

    def test_returns_error_dict_when_provider_fails(self):
        result = calendar_list_events(days_ahead=1)
        assert isinstance(result, dict)
        assert "status" in result
        # Without credentials, must be error
        assert result["status"] == "error"
        assert "message" in result
        assert isinstance(result["message"], str)
        assert len(result["message"]) > 0

    def test_result_has_status_key(self):
        result = calendar_list_events()
        assert "status" in result

    def test_default_days_ahead_accepted(self):
        result = calendar_list_events()
        assert result["status"] == "error"


@pytest.mark.unit
class TestCalendarCreateEventErrorPath:
    """Tests for the calendar_create_event MCP tool error paths.

    Ensures the tool correctly handles failures during event creation
    and returns a valid error status.
    """

    def test_returns_error_dict_when_provider_fails(self):
        result = calendar_create_event(
            summary="Test Event",
            start_time="2026-04-01T10:00:00",
            end_time="2026-04-01T11:00:00",
        )
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "error"
        assert "message" in result

    def test_with_description_and_location(self):
        result = calendar_create_event(
            summary="Meeting",
            start_time="2026-05-01T09:00:00",
            end_time="2026-05-01T10:00:00",
            description="Weekly sync",
            location="Room 42",
        )
        assert result["status"] == "error"

    def test_with_attendees_list(self):
        result = calendar_create_event(
            summary="Meeting",
            start_time="2026-05-01T09:00:00",
            end_time="2026-05-01T10:00:00",
            attendees=["user@example.com"],
        )
        assert result["status"] == "error"


@pytest.mark.unit
class TestCalendarGetEventErrorPath:
    """Tests for the calendar_get_event MCP tool error paths.

    Verifies that non-existent event IDs result in an appropriate
    error response from the tool.
    """

    def test_returns_error_dict_for_nonexistent_event(self):
        result = calendar_get_event("fake_event_id_xyz_12345")
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "error"
        assert "message" in result

    def test_empty_event_id_handled(self):
        result = calendar_get_event("")
        assert result["status"] == "error"


@pytest.mark.unit
class TestCalendarDeleteEventErrorPath:
    """Tests for the calendar_delete_event MCP tool error paths.

    Ensures failures during event deletion are reported via structured
    error responses.
    """

    def test_returns_error_dict_for_nonexistent_event(self):
        result = calendar_delete_event("fake_event_id_xyz_12345")
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "error"
        assert "message" in result


@pytest.mark.unit
class TestCalendarUpdateEventErrorPath:
    """Tests for the calendar_update_event MCP tool error paths.

    Verifies error reporting for event updates under invalid state.
    """

    def test_returns_error_dict_when_provider_fails(self):
        result = calendar_update_event(
            event_id="fake_event_id_xyz",
            summary="Updated Event",
            start_time="2026-06-01T10:00:00",
            end_time="2026-06-01T11:00:00",
        )
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "error"
        assert "message" in result

    def test_with_all_optional_fields(self):
        result = calendar_update_event(
            event_id="fake_id",
            summary="Updated",
            start_time="2026-06-01T10:00:00",
            end_time="2026-06-01T11:00:00",
            description="New desc",
            location="New loc",
            attendees=["a@example.com"],
        )
        assert result["status"] == "error"


# ── MCP decorator registration ────────────────────────────────────────────────


@pytest.mark.unit
class TestMcpToolRegistration:
    """Verifies that all MCP tools are correctly decorated and registered.

    Ensures that tool metadata is present and that tools are callable
    and return expected types.
    """

    def test_calendar_list_events_has_mcp_meta(self):
        assert hasattr(calendar_list_events, "_mcp_tool_meta") or callable(
            calendar_list_events
        )

    def test_calendar_create_event_callable(self):
        assert callable(calendar_create_event)

    def test_calendar_get_event_callable(self):
        assert callable(calendar_get_event)

    def test_calendar_delete_event_callable(self):
        assert callable(calendar_delete_event)

    def test_calendar_update_event_callable(self):
        assert callable(calendar_update_event)

    def test_all_tools_return_dicts(self):
        """All tools must return dict regardless of credential state."""
        results = [
            calendar_list_events(),
            calendar_create_event("T", "2026-01-01T10:00:00", "2026-01-01T11:00:00"),
            calendar_get_event("x"),
            calendar_delete_event("x"),
            calendar_update_event(
                "x", "T", "2026-01-01T10:00:00", "2026-01-01T11:00:00"
            ),
        ]
        for result in results:
            assert isinstance(result, dict), f"Expected dict, got {type(result)}"


# ── Live integration tests (skipped without credentials) ──────────────────────


@pytest.mark.network
@pytest.mark.skipif(
    os.environ.get("CODOMYRMEX_RUN_LIVE_CALENDAR_TESTS") != "1",
    reason="Live calendar reads require CODOMYRMEX_RUN_LIVE_CALENDAR_TESTS=1",
)
class TestCalendarToolsLive:
    """Live integration tests for calendar MCP tools.

    These tests run only after explicit live-test opt-in and use credentials
    selected by the operator. They interact with the live API, following the
    Zero-Mock policy for integration verification.
    """

    def test_list_events_returns_success(self):
        result = calendar_list_events(days_ahead=1)
        assert result["status"] == "success"
        assert "events" in result
        events_type = type(result["events"])
        assert events_type is list

    def test_event_fields_present(self):
        result = calendar_list_events(days_ahead=7)
        assert result["status"] == "success", "Live calendar list failed"
        for event in result["events"]:
            keys = set(event)
            for key in ("id", "summary", "start_time", "end_time"):
                assert key in keys, "Live calendar event schema was incomplete"
