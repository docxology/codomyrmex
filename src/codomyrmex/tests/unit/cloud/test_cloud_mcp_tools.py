"""Zero-mock tests for cloud MCP tool functions."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestGWSSDKSheetsGetValuesTool:
    """gws_sdk_sheets_get_values() returns a dict; error path when no creds."""

    def test_returns_dict(self) -> None:
        """Function should return a dictionary."""
        from codomyrmex.cloud.mcp_tools import gws_sdk_sheets_get_values

        result = gws_sdk_sheets_get_values("spreadsheet-id", "Sheet1!A1:D10")
        assert isinstance(result, dict)

    def test_has_status_key(self) -> None:
        """Function response should include a status key."""
        from codomyrmex.cloud.mcp_tools import gws_sdk_sheets_get_values

        result = gws_sdk_sheets_get_values("spreadsheet-id", "Sheet1!A1:D10")
        assert "status" in result

    def test_error_path_when_no_credentials(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Function should return error status when Google credentials are not configured."""
        from codomyrmex.cloud.mcp_tools import gws_sdk_sheets_get_values

        monkeypatch.delenv("GWS_SERVICE_ACCOUNT_FILE", raising=False)
        monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)

        result = gws_sdk_sheets_get_values("sid", "A1:B2")
        assert result["status"] == "error"
        assert "message" in result
        assert "credentials" in result["message"].lower()
