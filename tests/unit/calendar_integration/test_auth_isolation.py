"""Real selected credential files and transports, without remote API requests."""

import json
import os
from pathlib import Path

import pytest

from codomyrmex.calendar_integration.exceptions import CalendarAuthError
from codomyrmex.calendar_integration.gcal.provider import (
    GCAL_AVAILABLE,
    GoogleCalendar,
    _calendar_token_path,
)
from codomyrmex.calendar_integration.mcp_tools import _get_provider

pytestmark = pytest.mark.unit


def test_selected_missing_token_never_reverts_to_home(tmp_path, monkeypatch):
    selected = tmp_path / "selected-missing.json"
    monkeypatch.setenv("GOOGLE_CALENDAR_TOKEN_FILE", str(selected))
    assert _calendar_token_path() == selected
    assert not selected.exists()


def test_empty_selected_token_is_explicit_configuration_error(monkeypatch):
    monkeypatch.setenv("GOOGLE_CALENDAR_TOKEN_FILE", " ")
    with pytest.raises(CalendarAuthError, match="must not be empty"):
        _calendar_token_path()


@pytest.mark.skipif(not GCAL_AVAILABLE, reason="Google Calendar SDK is not installed")
def test_empty_selected_token_preserves_provider_and_mcp_error_contract(monkeypatch):
    monkeypatch.setenv("GOOGLE_CALENDAR_TOKEN_FILE", "")
    with pytest.raises(CalendarAuthError, match="must not be empty"):
        GoogleCalendar.from_env()
    with pytest.raises(RuntimeError, match="must not be empty"):
        _get_provider()


@pytest.mark.skipif(not GCAL_AVAILABLE, reason="Google Calendar SDK is not installed")
@pytest.mark.parametrize("factory", [_get_provider, GoogleCalendar.from_env])
def test_selected_token_configures_real_closed_transport(
    factory, tmp_path, monkeypatch
):
    """Static Google discovery builds the actual transport without API execution."""
    selected = tmp_path / "selected-token.json"
    selected.write_text(
        json.dumps(
            {"access_token": "local-test-access", "refresh_token": "local-test-refresh"}
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("GOOGLE_CALENDAR_TOKEN_FILE", str(selected))
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "local-test-client")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "local-test-secret")
    provider = factory()
    try:
        credentials = provider.service._http.credentials
        assert credentials.token == "local-test-access"
        assert credentials.refresh_token == "local-test-refresh"
        assert credentials.client_id == "local-test-client"
    finally:
        provider.close()
    # HOME is neither redirected nor used as a test credential source.
    assert _calendar_token_path() == selected


@pytest.mark.skipif(not GCAL_AVAILABLE, reason="Google Calendar SDK is not installed")
@pytest.mark.parametrize("factory", [_get_provider, GoogleCalendar.from_env])
def test_env_oauth_priority_does_not_read_selected_malformed_file(
    factory, tmp_path, monkeypatch
):
    selected = tmp_path / "invalid-json.json"
    selected.write_text("Not JSON", encoding="utf-8")
    monkeypatch.setenv("GOOGLE_CALENDAR_TOKEN_FILE", str(selected))
    for name, value in (
        ("GOOGLE_CLIENT_ID", "local-test-client"),
        ("GOOGLE_CLIENT_SECRET", "local-test-secret"),
        ("GOOGLE_REFRESH_TOKEN", "local-test-env-refresh"),
    ):
        monkeypatch.setenv(name, value)
    provider = factory()
    try:
        assert (
            provider.service._http.credentials.refresh_token == "local-test-env-refresh"
        )
    finally:
        provider.close()


@pytest.mark.skipif(not GCAL_AVAILABLE, reason="Google Calendar SDK is not installed")
def test_explicit_missing_adc_fails_before_home_or_metadata_lookup():
    with pytest.raises(CalendarAuthError) as failure:
        GoogleCalendar.from_env()
    assert "absent-adc.json" in str(failure.value)
    assert not Path(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]).exists()
