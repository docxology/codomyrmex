"""Custom exceptions for the calendar module."""

class CalendarError(Exception):
    """Base exception for all calendar-related errors."""
    pass

class CalendarAuthError(CalendarError):
    """Raised when authentication with the calendar provider fails."""
    pass

class CalendarAPIError(CalendarError):
    """Raised when the calendar provider API returns an error."""
    pass

class EventNotFoundError(CalendarError):
    """Raised when a requested calendar event is not found."""
    pass

class InvalidEventError(CalendarError):
    """Raised when event data is invalid or missing required fields."""
    pass
