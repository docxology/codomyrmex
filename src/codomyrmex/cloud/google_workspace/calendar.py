"""Google Calendar SDK client."""

from __future__ import annotations

from typing import Any

from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GoogleCalendarClient(GoogleWorkspaceBase):
    """Client for Google Calendar API v3."""

    _api_name = "calendar"
    _api_version = "v3"

    def list_events(
        self,
        calendar_id: str = "primary",
        time_min: str = "",
        time_max: str = "",
        max_results: int = 20,
    ) -> list[dict[str, Any]]:
        """list calendar events in an optional date range.

        Args:
            calendar_id: Calendar ID (default: 'primary').
            time_min: RFC3339 lower bound for event start time.
            time_max: RFC3339 upper bound for event start time.
            max_results: Maximum number of events to return.

        Returns:
            list of event dicts.
        """
        params: dict[str, Any] = {
            "calendarId": calendar_id,
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime",
        }
        if time_min:
            params["timeMin"] = time_min
        if time_max:
            params["timeMax"] = time_max

        def _call():
            return self._get_service().events().list(**params).execute()

        result = self._safe_call(_call, "list", "events", default={})
        return result.get("items", []) if isinstance(result, dict) else []

    def create_event(
        self,
        summary: str,
        start: str,
        end: str,
        calendar_id: str = "primary",
        description: str = "",
        attendees: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a calendar event.

        Args:
            summary: Event title.
            start: Start datetime in RFC3339 format (e.g., '2026-03-05T10:00:00Z').
            end: End datetime in RFC3339 format.
            calendar_id: Calendar ID (default: 'primary').
            description: Event description.
            attendees: list of attendee email addresses.

        Returns:
            Created event dict, or empty dict on error.
        """
        event: dict[str, Any] = {
            "summary": summary,
            "start": {"dateTime": start, "timeZone": "UTC"},
            "end": {"dateTime": end, "timeZone": "UTC"},
        }
        if description:
            event["description"] = description
        if attendees:
            event["attendees"] = [{"email": a} for a in attendees]

        def _call():
            return (
                self._get_service()
                .events()
                .insert(calendarId=calendar_id, body=event)
                .execute()
            )

        return self._safe_call(_call, "create", "event", default={}) or {}
