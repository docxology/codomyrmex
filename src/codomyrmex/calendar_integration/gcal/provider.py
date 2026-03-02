"""Google Calendar implementation of the CalendarProvider interface."""

import logging
import os
from datetime import datetime

try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger
    logger = get_logger(__name__)
except Exception:
    logger = logging.getLogger(__name__)

from codomyrmex.calendar_integration.exceptions import (
    CalendarAPIError,
    CalendarAuthError,
    EventNotFoundError,
    InvalidEventError,
)
from codomyrmex.calendar_integration.generics import CalendarEvent, CalendarProvider

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import Resource, build
    from googleapiclient.errors import HttpError
    GCAL_AVAILABLE = True
except ImportError:
    Credentials = None
    Resource = None
    HttpError = Exception
    build = None
    GCAL_AVAILABLE = False

_GCAL_SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendar(CalendarProvider):
    """Google Calendar provider implementation."""

    def __init__(self, credentials: Credentials | None = None, service: Resource | None = None):
        """
        Initialize the Google Calendar provider.

        Args:
            credentials: A google.oauth2.credentials.Credentials object.
            service: A pre-built and authenticated Google Calendar API resource object.
        """
        if not GCAL_AVAILABLE:
            raise ImportError(
                "Google Calendar dependencies are not installed. "
                "Please install codomyrmex with the 'calendar' extra: uv sync --extra calendar"
            )

        if not credentials and not service:
            raise CalendarAuthError("Either credentials or a built service object must be provided.")

        try:
            self.service = service or build('calendar', 'v3', credentials=credentials)
        except Exception as e:
            raise CalendarAuthError(f"Failed to initialize Google Calendar API service: {e}") from e

    @classmethod
    def from_env(cls) -> "GoogleCalendar":
        """Create a GoogleCalendar from environment variables.

        Tries GOOGLE_REFRESH_TOKEN + GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET first,
        then token file (~/.codomyrmex/gcal_token.json),
        then falls back to Application Default Credentials.

        Raises:
            ImportError: If Google Calendar dependencies are not installed.
            CalendarAuthError: If no valid credentials are available.
        """
        if not GCAL_AVAILABLE:
            raise ImportError(
                "Google Calendar dependencies are not installed. "
                "Run: uv sync --extra calendar"
            )

        refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        if refresh_token and client_id and client_secret:
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=_GCAL_SCOPES,
            )
            return cls(credentials=creds)

        # Option 1b: Token file from PMServer OAuth flow
        import json
        from pathlib import Path

        token_path = Path.home() / ".codomyrmex" / "gcal_token.json"
        if token_path.exists() and client_id and client_secret:
            try:
                token_data = json.loads(token_path.read_text())
                file_refresh = token_data.get("refresh_token")
                if file_refresh:
                    creds = Credentials(
                        token=token_data.get("access_token"),
                        refresh_token=file_refresh,
                        token_uri="https://oauth2.googleapis.com/token",
                        client_id=client_id,
                        client_secret=client_secret,
                        scopes=_GCAL_SCOPES,
                    )
                    return cls(credentials=creds)
            except (json.JSONDecodeError, OSError) as e:
                logger.debug("Service account credentials unavailable, falling through to ADC: %s", e)
                pass  # fall through to ADC

        try:
            import google.auth  # noqa: PLC0415 — conditional import
            creds, _ = google.auth.default(scopes=_GCAL_SCOPES)
            return cls(credentials=creds)
        except Exception as e:
            raise CalendarAuthError(
                "No Google Calendar credentials found. Set GOOGLE_CLIENT_ID + "
                "GOOGLE_CLIENT_SECRET + GOOGLE_REFRESH_TOKEN env vars, "
                "or place a token file at ~/.codomyrmex/gcal_token.json, "
                f"or configure GOOGLE_APPLICATION_CREDENTIALS: {e}"
            ) from e

    def _event_to_gcal_dict(self, event: CalendarEvent) -> dict:
        """Serialize a ``CalendarEvent`` to the Google Calendar API request body.

        Args:
            event: The event to serialize.  ``start_time`` and ``end_time``
                must be timezone-aware; their ``isoformat()`` is used verbatim
                for the ``dateTime`` field.

        Returns:
            A dict suitable for the ``body`` argument of
            ``service.events().insert()`` or ``service.events().update()``.
            Shape::

                {
                    "summary": str,
                    "start": {"dateTime": str},
                    "end":   {"dateTime": str},
                    # Optional fields — only present when non-None / non-empty:
                    "description": str,
                    "location":    str,
                    "attendees":   [{"email": str}, ...],
                }

            Optional fields (``description``, ``location``, ``attendees``) are
            omitted entirely when the corresponding attribute is ``None`` or an
            empty list — they are **not** set to ``null`` or ``[]``.
        """
        body = {
            'summary': event.summary,
            'start': {'dateTime': event.start_time.isoformat()},
            'end': {'dateTime': event.end_time.isoformat()},
        }
        if event.description is not None:
            body['description'] = event.description
        if event.location is not None:
            body['location'] = event.location
        if event.attendees:
            body['attendees'] = [{'email': email} for email in event.attendees]
        return body

    def _gcal_dict_to_event(self, item: dict) -> CalendarEvent:
        """Deserialize a Google Calendar API response dict into a ``CalendarEvent``.

        Handles two datetime representations returned by the API:

        * **Timed events** — ``item["start"]["dateTime"]`` is an ISO 8601
          string with timezone offset (e.g. ``"2026-02-24T10:00:00-08:00"``).
          The legacy ``Z`` suffix (UTC) is normalized to ``+00:00`` so
          ``datetime.fromisoformat`` accepts it on Python < 3.11.
        * **All-day events** — ``item["start"]["date"]`` is a plain date
          string (``"2026-02-24"``); ``fromisoformat`` parses it without
          timezone info.  Consumers should treat such events as full-day spans.

        Special cases:

        * **Missing title** — When ``item["summary"]`` is absent, the
          ``CalendarEvent.summary`` field defaults to ``"(No title)"``.
        * **Attendees** — Extracted from the ``"attendees"`` list of dicts;
          only entries containing an ``"email"`` key are included.  Entries
          without ``"email"`` are silently skipped.
        * **``Z`` normalization** — ``"...Z"`` → ``"...+00:00"`` substitution
          applied to both ``start`` and ``end`` strings before parsing.

        Args:
            item: A raw event dict from the Google Calendar API
                (``events.list``, ``events.get``, ``events.insert``, etc.).

        Returns:
            A populated ``CalendarEvent`` with ``id``, ``summary``,
            ``start_time``, ``end_time``, ``description``, ``location``,
            ``attendees``, and ``html_link`` set from ``item``.

        Raises:
            InvalidEventError: If required keys (``start``, ``end``) are
                missing or if the datetime strings cannot be parsed.
        """
        try:
            # Handle start/end which can be either 'dateTime' or 'date' (all-day event)
            start_str = item['start'].get('dateTime', item['start'].get('date'))
            end_str = item['end'].get('dateTime', item['end'].get('date'))

            start_time = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_str.replace('Z', '+00:00'))

            attendees = [attendee.get('email') for attendee in item.get('attendees', []) if 'email' in attendee]

            return CalendarEvent(
                id=item.get('id'),
                summary=item.get('summary', '(No title)'),
                description=item.get('description'),
                start_time=start_time,
                end_time=end_time,
                location=item.get('location'),
                attendees=attendees,
                html_link=item.get('htmlLink')
            )
        except (KeyError, ValueError) as e:
            raise InvalidEventError(f"Failed to parse Google Calendar event data: {e}") from e

    def list_events(self, time_min: datetime, time_max: datetime, calendar_id: str = 'primary') -> list[CalendarEvent]:
        """List events between the given start and end times."""
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + ('Z' if not time_min.tzinfo else ''),
                timeMax=time_max.isoformat() + ('Z' if not time_max.tzinfo else ''),
                maxResults=2500,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            items = events_result.get('items', [])
            return [self._gcal_dict_to_event(item) for item in items]
        except HttpError as e:
            raise CalendarAPIError(f"Failed to list events: {e}") from e

    def create_event(self, event: CalendarEvent, calendar_id: str = 'primary') -> CalendarEvent:
        """Create a new event in the calendar."""
        body = self._event_to_gcal_dict(event)
        try:
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=body
            ).execute()
            return self._gcal_dict_to_event(created_event)
        except HttpError as e:
            raise CalendarAPIError(f"Failed to create event: {e}") from e

    def get_event(self, event_id: str, calendar_id: str = 'primary') -> CalendarEvent:
        """Fetch a specific event by its ID."""
        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return self._gcal_dict_to_event(event)
        except HttpError as e:
            if e.resp.status == 404:
                raise EventNotFoundError(f"Event with ID {event_id} not found.") from e
            raise CalendarAPIError(f"Failed to fetch event: {e}") from e

    def update_event(self, event_id: str, event: CalendarEvent, calendar_id: str = 'primary') -> CalendarEvent:
        """Update an existing event."""
        body = self._event_to_gcal_dict(event)
        try:
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=body
            ).execute()
            return self._gcal_dict_to_event(updated_event)
        except HttpError as e:
            if e.resp.status == 404:
                raise EventNotFoundError(f"Event with ID {event_id} not found for update.") from e
            raise CalendarAPIError(f"Failed to update event: {e}") from e

    def delete_event(self, event_id: str, calendar_id: str = 'primary') -> None:
        """Delete an event from the calendar."""
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                raise EventNotFoundError(f"Event with ID {event_id} not found for deletion.") from e
            raise CalendarAPIError(f"Failed to delete event: {e}") from e
