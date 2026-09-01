import pytest

from codomyrmex.cloud.google_workspace.calendar import GoogleCalendarClient
from codomyrmex.cloud.mcp_tools import gws_sdk_calendar_list_events


class TestGWSSdkCalendarListEvents:
    def test_returns_dict(self):
        """Test that the function returns a dict even on failure."""
        result = gws_sdk_calendar_list_events()
        assert isinstance(result, dict)

    def test_error_path_when_no_env(self):
        """Test that the function returns an error status when env is not set."""
        result = gws_sdk_calendar_list_events()
        assert result["status"] == "error"
        assert "message" in result

    def test_success_path_with_mocked_client(self, monkeypatch: pytest.MonkeyPatch):
        """Test the successful execution path with a mocked client."""

        class DummyClient:
            def list_events(self, calendar_id, time_min, time_max):
                return [{"id": "123", "summary": "Meeting"}]

        monkeypatch.setattr(GoogleCalendarClient, "from_env", DummyClient)

        result = gws_sdk_calendar_list_events(calendar_id="primary")
        assert result["status"] == "success"
        assert result["count"] == 1
        assert result["events"][0]["summary"] == "Meeting"

    def test_error_path_with_exception_in_mock(self, monkeypatch: pytest.MonkeyPatch):
        """Test that an exception during client call returns an error status."""

        class DummyClient:
            def list_events(self, calendar_id, time_min, time_max):
                raise ValueError("Mocked error")

        monkeypatch.setattr(GoogleCalendarClient, "from_env", DummyClient)

        result = gws_sdk_calendar_list_events(calendar_id="primary")
        assert result["status"] == "error"
        assert "Mocked error" in result["message"]
