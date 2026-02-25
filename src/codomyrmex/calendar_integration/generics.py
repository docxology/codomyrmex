"""Generic representations and base classes for the calendar module."""

import abc
from datetime import datetime

from pydantic import BaseModel, Field


class CalendarEvent(BaseModel):
    """A generic representation of a calendar event.

    All ``datetime`` fields (``start_time``, ``end_time``) **must** be
    timezone-aware.  Pass naive datetimes through
    ``dt.replace(tzinfo=timezone.utc)`` or use ``zoneinfo.ZoneInfo`` before
    constructing this model.  Provider implementations may raise
    ``InvalidEventError`` when they receive timezone-naive values.
    """

    id: str | None = Field(default=None, description="Provider-assigned event ID; None for unsaved events.")
    summary: str = Field(description="Event title shown in calendar UIs.")
    description: str | None = Field(default=None, description="Free-text body or agenda for the event.")
    start_time: datetime = Field(description="Timezone-aware start datetime of the event.")
    end_time: datetime = Field(description="Timezone-aware end datetime of the event.")
    location: str | None = Field(default=None, description="Physical or virtual location string.")
    attendees: list[str] = Field(default_factory=list, description="List of attendee email addresses.")
    html_link: str | None = Field(default=None, description="URL to open the event in a browser (provider-assigned).")


class CalendarProvider(abc.ABC):
    """Abstract base class for all calendar providers."""

    @abc.abstractmethod
    def list_events(self, time_min: datetime, time_max: datetime) -> list[CalendarEvent]:
        """List events within a time window.

        Args:
            time_min: Inclusive start of the query window (timezone-aware).
            time_max: Exclusive end of the query window (timezone-aware).

        Returns:
            List of ``CalendarEvent`` objects ordered by start time, possibly
            empty if no events exist in the window.

        Raises:
            CalendarAuthError: If credentials are invalid or expired.
            CalendarAPIError: If the provider returns an unexpected error.
        """

    @abc.abstractmethod
    def create_event(self, event: CalendarEvent) -> CalendarEvent:
        """Create a new event and return the saved version with provider ID.

        Args:
            event: Fully populated ``CalendarEvent``.  The ``id`` field is
                ignored; the provider assigns a new ID.

        Returns:
            A new ``CalendarEvent`` with ``id`` and ``html_link`` populated by
            the provider.

        Raises:
            CalendarAuthError: If credentials are invalid or expired.
            CalendarAPIError: If the provider rejects the payload.
        """

    @abc.abstractmethod
    def get_event(self, event_id: str) -> CalendarEvent:
        """Fetch a single event by its provider-assigned ID.

        Args:
            event_id: The provider's opaque event identifier.

        Returns:
            The matching ``CalendarEvent``.

        Raises:
            EventNotFoundError: If no event with ``event_id`` exists.
            CalendarAuthError: If credentials are invalid or expired.
            CalendarAPIError: On unexpected provider errors.
        """

    @abc.abstractmethod
    def update_event(self, event_id: str, event: CalendarEvent) -> CalendarEvent:
        """Replace all fields of an existing event (PUT semantics).

        The provider overwrites every mutable field with the values from
        ``event``; fields omitted from ``event`` are not preserved from the
        prior version.

        Args:
            event_id: The provider ID of the event to update.
            event: New field values.  The ``id`` field of ``event`` is ignored;
                ``event_id`` controls which resource is targeted.

        Returns:
            The updated ``CalendarEvent`` as returned by the provider.

        Raises:
            EventNotFoundError: If ``event_id`` does not exist.
            CalendarAuthError: If credentials are invalid or expired.
            CalendarAPIError: On unexpected provider errors.
        """

    @abc.abstractmethod
    def delete_event(self, event_id: str) -> None:
        """Permanently delete an event from the calendar.

        Args:
            event_id: The provider-assigned ID of the event to delete.

        Returns:
            None on success.

        Raises:
            EventNotFoundError: If ``event_id`` does not exist.
            CalendarAuthError: If credentials are invalid or expired.
            CalendarAPIError: On unexpected provider errors.
        """
