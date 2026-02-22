"""Generic representations and base classes for the calendar module."""

import abc
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class CalendarEvent(BaseModel):
    """A generic representation of a calendar event."""
    id: Optional[str] = None
    summary: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)
    html_link: Optional[str] = None


class CalendarProvider(abc.ABC):
    """Abstract base class for all calendar providers."""

    @abc.abstractmethod
    def list_events(self, time_min: datetime, time_max: datetime) -> List[CalendarEvent]:
        """List events between the given start and end times."""
        pass

    @abc.abstractmethod
    def create_event(self, event: CalendarEvent) -> CalendarEvent:
        """Create a new event in the calendar."""
        pass

    @abc.abstractmethod
    def get_event(self, event_id: str) -> CalendarEvent:
        """Fetch a specific event by its ID."""
        pass

    @abc.abstractmethod
    def update_event(self, event_id: str, event: CalendarEvent) -> CalendarEvent:
        """Update an existing event."""
        pass

    @abc.abstractmethod
    def delete_event(self, event_id: str) -> None:
        """Delete an event from the calendar."""
        pass
