"""MCP tools for interacting with Google Calendar.

This module exposes the Codomyrmex calendar provider (with Google Calendar backend)
as MCP tools, enabling agents to schedule, read, and manage events.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs: Any):  # type: ignore
        """Execute Mcp Tool operations natively."""
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func
        return decorator

from codomyrmex.calendar_integration.generics import CalendarEvent


def _get_provider() -> Any:
    """Initialize the GoogleCalendar provider from PAI OAuth token and env vars.

    Returns:
        A configured ``GoogleCalendar`` instance ready for API calls.

    Raises:
        RuntimeError: Under four conditions —
            1. **Missing dependencies** — Google Calendar packages not installed.
               Fix: ``uv sync --extra calendar``.
            2. **No token file** — ``~/.codomyrmex/gcal_token.json`` does not
               exist.  Fix: authenticate via the PAI dashboard first.
            3. **Malformed token** — The token file exists but cannot be parsed
               as JSON or is missing required fields (``access_token``/
               ``refresh_token``).
            4. **Missing env vars** — ``GOOGLE_CLIENT_ID`` or
               ``GOOGLE_CLIENT_SECRET`` are not set.  Load them from a ``.env``
               file or export them in the shell before invoking MCP tools.
    """
    try:
        from google.oauth2.credentials import Credentials
        from codomyrmex.calendar_integration.gcal.provider import GoogleCalendar
    except ImportError:
        raise RuntimeError("Google Calendar dependencies not installed. Run `uv sync --extra calendar`")

    token_path = Path.home() / ".codomyrmex" / "gcal_token.json"
    if not token_path.exists():
        raise RuntimeError("Google Calendar not authenticated. Please connect via PAI dashboard.")

    try:
        with open(token_path, "r") as f:
            token_data = json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to read calendar token: {e}")

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError("GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET environment variables are missing.")

    creds = Credentials(
        token=token_data.get("access_token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/calendar"]
    )

    return GoogleCalendar(credentials=creds)


@mcp_tool(
    category="calendar",
    description="List upcoming events from the calendar.",
)
def calendar_list_events(days_ahead: int = 7) -> Dict[str, Any]:
    """List calendar events for the next given number of days.

    Args:
        days_ahead: Number of days into the future to query (default 7).

    Returns:
        ``{"status": "ok", "events": [...]}`` on success, where each event is a
        dict with keys ``id``, ``summary``, ``start_time``, ``end_time``,
        ``description``, ``location``, ``attendees``, ``html_link``.
        ``{"status": "error", "error": "<message>"}`` on failure — check
        ``result["status"]`` before accessing other keys.
    """
    try:
        provider = _get_provider()
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=days_ahead)
        
        events = provider.list_events(time_min=now, time_max=future)
        return {
            "status": "ok", 
            "events": [
                {
                    "id": e.id,
                    "summary": e.summary,
                    "start_time": e.start_time.isoformat(),
                    "end_time": e.end_time.isoformat(),
                    "description": e.description,
                    "location": e.location,
                    "attendees": e.attendees,
                    "html_link": e.html_link
                } for e in events
            ]
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="calendar",
    description=(
        "Create a new calendar event. "
        "danielarifriedman@gmail.com is automatically injected as an attendee "
        "on every event regardless of the attendees parameter."
    ),
)
def calendar_create_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
    attendees: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Create a new event in the Google Calendar.

    ``danielarifriedman@gmail.com`` is always added to ``attendees`` before the
    API call, even when ``attendees=[]`` or ``attendees=None``.

    Args:
        summary: Event title displayed in the calendar.
        start_time: ISO 8601 string, e.g. ``"2026-02-24T10:00:00Z"``.
        end_time: ISO 8601 string, e.g. ``"2026-02-24T11:00:00Z"``.
        description: Free-text event description (default empty string).
        location: Physical or virtual location (default empty string).
        attendees: Additional email addresses to invite.  Daniel's address is
            always appended automatically.

    Returns:
        ``{"status": "ok", "event_id": "<id>", "link": "<url>"}`` on success.
        ``{"status": "error", "error": "<message>"}`` on failure.
    """
    try:
        provider = _get_provider()
        
        # Ensure Daniel is included if attendees is empty
        if attendees is None:
            attendees = ["danielarifriedman@gmail.com"]
        elif "danielarifriedman@gmail.com" not in attendees:
            attendees.append("danielarifriedman@gmail.com")
            
        evt = CalendarEvent(
            summary=summary,
            description=description,
            start_time=datetime.fromisoformat(start_time.replace('Z', '+00:00')),
            end_time=datetime.fromisoformat(end_time.replace('Z', '+00:00')),
            location=location,
            attendees=attendees
        )
        created = provider.create_event(evt)
        return {
            "status": "ok", 
            "event_id": created.id,
            "link": created.html_link
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="calendar",
    description="Get details of a specific calendar event by ID.",
)
def calendar_get_event(event_id: str) -> Dict[str, Any]:
    """Fetch details of a single calendar event by its provider ID.

    Args:
        event_id: The Google Calendar event ID (opaque string, e.g.
            ``"abc123xyz_20260224T100000Z"``).

    Returns:
        ``{"status": "ok", "event": {<event dict>}}`` on success, where the
        event dict has keys: ``id``, ``summary``, ``start_time``, ``end_time``,
        ``description``, ``location``, ``attendees``, ``html_link``.
        ``{"status": "error", "error": "<message>"}`` if the event is not found
        or on API failure.
    """
    try:
        provider = _get_provider()
        e = provider.get_event(event_id)
        return {
            "status": "ok", 
            "event": {
                "id": e.id,
                "summary": e.summary,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat(),
                "description": e.description,
                "location": e.location,
                "attendees": e.attendees,
                "html_link": e.html_link
            }
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="calendar",
    description="Delete a calendar event by ID.",
)
def calendar_delete_event(event_id: str) -> Dict[str, Any]:
    """Permanently delete an event from the calendar.

    Args:
        event_id: The Google Calendar event ID to delete.

    Returns:
        ``{"status": "ok", "deleted": True}`` on success.
        ``{"status": "error", "error": "<message>"}`` if the event is not found
        or on API failure.
    """
    try:
        provider = _get_provider()
        provider.delete_event(event_id)
        return {"status": "ok", "deleted": True}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="calendar",
    description=(
        "Update an existing calendar event (PUT semantics — all fields replaced). "
        "danielarifriedman@gmail.com is automatically injected as an attendee "
        "on every update regardless of the attendees parameter."
    ),
)
def calendar_update_event(
    event_id: str,
    summary: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
    attendees: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Replace all fields of an existing calendar event (PUT semantics).

    All fields are overwritten on the server; fields not supplied here are not
    preserved from the prior version of the event.  ``danielarifriedman@gmail.com``
    is always added to ``attendees`` before the API call.

    Args:
        event_id: The Google Calendar event ID to update.
        summary: Replacement event title.
        start_time: ISO 8601 string, e.g. ``"2026-02-24T10:00:00Z"``.
        end_time: ISO 8601 string, e.g. ``"2026-02-24T11:00:00Z"``.
        description: Replacement event description (default empty string).
        location: Replacement location (default empty string).
        attendees: Replacement attendee list.  Daniel's address is always
            appended automatically.

    Returns:
        ``{"status": "ok", "event_id": "<id>", "link": "<url>"}`` on success.
        ``{"status": "error", "error": "<message>"}`` if the event is not found
        or on API failure.
    """
    try:
        provider = _get_provider()
        
        # Ensure Daniel is included if attendees is empty
        if attendees is None:
            attendees = ["danielarifriedman@gmail.com"]
        elif "danielarifriedman@gmail.com" not in attendees:
            attendees.append("danielarifriedman@gmail.com")
            
        evt = CalendarEvent(
            summary=summary,
            description=description,
            start_time=datetime.fromisoformat(start_time.replace('Z', '+00:00')),
            end_time=datetime.fromisoformat(end_time.replace('Z', '+00:00')),
            location=location,
            attendees=attendees
        )
        updated_event = provider.update_event(event_id, evt)
        return {
            "status": "ok", 
            "event_id": updated_event.id,
            "link": updated_event.html_link
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}

