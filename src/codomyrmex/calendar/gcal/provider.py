"""Google Calendar implementation of the CalendarProvider interface."""

from datetime import datetime
from typing import List, Optional

from ..exceptions import CalendarAPIError, CalendarAuthError, EventNotFoundError, InvalidEventError
from ..generics import CalendarEvent, CalendarProvider

try:
    from googleapiclient.discovery import build, Resource
    from googleapiclient.errors import HttpError
    from google.oauth2.credentials import Credentials
    GCAL_AVAILABLE = True
except ImportError:
    Credentials = None
    Resource = None
    HttpError = Exception
    build = None
    GCAL_AVAILABLE = False


class GoogleCalendar(CalendarProvider):
    """Google Calendar provider implementation."""

    def __init__(self, credentials: Optional[Credentials] = None, service: Optional[Resource] = None):
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
            raise CalendarAuthError(f"Failed to initialize Google Calendar API service: {e}")

    def _event_to_gcal_dict(self, event: CalendarEvent) -> dict:
        """Convert a CalendarEvent to the Google Calendar API format."""
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
        """Convert a Google Calendar API dictionary to a CalendarEvent."""
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
            raise InvalidEventError(f"Failed to parse Google Calendar event data: {e}")

    def list_events(self, time_min: datetime, time_max: datetime, calendar_id: str = 'primary') -> List[CalendarEvent]:
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
            raise CalendarAPIError(f"Failed to list events: {e}")

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
            raise CalendarAPIError(f"Failed to create event: {e}")

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
                raise EventNotFoundError(f"Event with ID {event_id} not found.")
            raise CalendarAPIError(f"Failed to fetch event: {e}")

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
                raise EventNotFoundError(f"Event with ID {event_id} not found for update.")
            raise CalendarAPIError(f"Failed to update event: {e}")

    def delete_event(self, event_id: str, calendar_id: str = 'primary') -> None:
        """Delete an event from the calendar."""
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                raise EventNotFoundError(f"Event with ID {event_id} not found for deletion.")
            raise CalendarAPIError(f"Failed to delete event: {e}")
