"""Strictly zero-mock unit tests for calendar_integration MCP tools.

Tests behavior like missing tokens, bad dependencies, and environment variable behavior.
"""

from pathlib import Path

import pytest

from codomyrmex.calendar_integration.mcp_tools import (
    _get_provider,
    calendar_create_event,
    calendar_delete_event,
    calendar_get_event,
    calendar_list_events,
    calendar_update_event,
)


@pytest.fixture
def no_gcal_token(monkeypatch, tmp_path):
    """Fixture to ensure the token file does not exist during tests."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return tmp_path


def test_get_provider_no_token(no_gcal_token):
    """Test _get_provider raises RuntimeError when token file is missing."""
    with pytest.raises(RuntimeError, match="Google Calendar not authenticated"):
        _get_provider()


def test_calendar_list_events_error(no_gcal_token):
    """Test calendar_list_events returns error dict on failure."""
    result = calendar_list_events()
    assert result["status"] == "error"
    assert "Google Calendar not authenticated" in result["error"]


def test_calendar_create_event_error(no_gcal_token):
    """Test calendar_create_event returns error dict on failure."""
    result = calendar_create_event(
        summary="Test",
        start_time="2026-01-01T10:00:00Z",
        end_time="2026-01-01T11:00:00Z",
    )
    assert result["status"] == "error"
    assert "Google Calendar not authenticated" in result["error"]


def test_calendar_get_event_error(no_gcal_token):
    """Test calendar_get_event returns error dict on failure."""
    result = calendar_get_event(event_id="123")
    assert result["status"] == "error"
    assert "Google Calendar not authenticated" in result["error"]


def test_calendar_delete_event_error(no_gcal_token):
    """Test calendar_delete_event returns error dict on failure."""
    result = calendar_delete_event(event_id="123")
    assert result["status"] == "error"
    assert "Google Calendar not authenticated" in result["error"]


def test_calendar_update_event_error(no_gcal_token):
    """Test calendar_update_event returns error dict on failure."""
    result = calendar_update_event(
        event_id="123",
        summary="Test",
        start_time="2026-01-01T10:00:00Z",
        end_time="2026-01-01T11:00:00Z",
    )
    assert result["status"] == "error"
    assert "Google Calendar not authenticated" in result["error"]


def test_get_provider_missing_env_vars(no_gcal_token, monkeypatch, tmp_path):
    """Test _get_provider raises RuntimeError when env vars are missing."""
    token_dir = tmp_path / ".codomyrmex"
    token_dir.mkdir(exist_ok=True)
    token_file = token_dir / "gcal_token.json"
    token_file.write_text('{"access_token": "abc", "refresh_token": "def"}')

    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)

    with pytest.raises(
        RuntimeError,
        match="GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET environment variables are missing",
    ):
        _get_provider()


def test_get_provider_bad_json(no_gcal_token, monkeypatch, tmp_path):
    """Test _get_provider raises RuntimeError when token file is bad json."""
    token_dir = tmp_path / ".codomyrmex"
    token_dir.mkdir(exist_ok=True)
    token_file = token_dir / "gcal_token.json"
    token_file.write_text('{"access_token": "abc", "refresh_toke')

    with pytest.raises(RuntimeError, match="Failed to read calendar token"):
        _get_provider()
