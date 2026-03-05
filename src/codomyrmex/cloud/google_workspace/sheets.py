"""Google Sheets SDK client."""

from __future__ import annotations

from typing import Any

from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GoogleSheetsClient(GoogleWorkspaceBase):
    """Client for Google Sheets API v4."""

    _api_name = "sheets"
    _api_version = "v4"

    def get_values(
        self,
        spreadsheet_id: str,
        range_notation: str,
    ) -> list[list[Any]]:
        """Read values from a spreadsheet range.

        Args:
            spreadsheet_id: The ID of the spreadsheet.
            range_notation: A1 notation range (e.g., 'Sheet1!A1:D10').

        Returns:
            2D list of cell values, or empty list on error.
        """

        def _call():
            return (
                self._get_service()
                .spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=range_notation)
                .execute()
            )

        result = self._safe_call(_call, "get", "values", default={})
        return result.get("values", []) if isinstance(result, dict) else []

    def update_values(
        self,
        spreadsheet_id: str,
        range_notation: str,
        values: list[list[Any]],
        value_input_option: str = "USER_ENTERED",
    ) -> dict[str, Any]:
        """Write values to a spreadsheet range.

        Args:
            spreadsheet_id: The ID of the spreadsheet.
            range_notation: A1 notation range to write to.
            values: 2D list of values to write.
            value_input_option: How to parse values ('USER_ENTERED' or 'RAW').

        Returns:
            Update response dict, or empty dict on error.
        """
        body = {"values": values}

        def _call():
            return (
                self._get_service()
                .spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_notation,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )

        return self._safe_call(_call, "update", "values", default={}) or {}
