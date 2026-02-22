"""Calendar module for Codomyrmex.

This module provides generic calendar interfaces and a Google Calendar provider.

Submodules:
    - generics: Provides `CalendarEvent` and abstract `CalendarProvider`
    - gcal: Provides `GoogleCalendar` implementation

Installation:
    Install calendar dependencies with:
    ```bash
    uv sync --extra calendar
    ```
"""

__version__ = "0.1.0"

from .exceptions import (
    CalendarAPIError,
    CalendarAuthError,
    CalendarError,
    EventNotFoundError,
    InvalidEventError,
)
from .generics import CalendarEvent, CalendarProvider

try:
    from .gcal import GCAL_AVAILABLE, GoogleCalendar
    CALENDAR_AVAILABLE = True
except ImportError:
    GCAL_AVAILABLE = False
    CALENDAR_AVAILABLE = False
    GoogleCalendar = None  # type: ignore

def cli_commands():
    """Return CLI commands for the calendar module."""
    return {
        "status": {
            "help": "Check calendar module status and dependencies",
            "handler": lambda **kwargs: print(
                f"Calendar Module v{__version__}\n"
                f"  Available: {CALENDAR_AVAILABLE}\n"
                f"  Google Calendar: {GCAL_AVAILABLE}"
            ),
        }
    }

__all__ = [
    # API endpoints
    "CalendarProvider",
    "CalendarEvent",
    "GoogleCalendar",
    # Status flags
    "CALENDAR_AVAILABLE",
    "GCAL_AVAILABLE",
    # Exceptions
    "CalendarError",
    "CalendarAuthError",
    "CalendarAPIError",
    "EventNotFoundError",
    "InvalidEventError",
    # Utilities
    "cli_commands",
]
