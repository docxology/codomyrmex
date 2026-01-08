from datetime import datetime
from typing import Optional

import pytz

from codomyrmex.logging_monitoring.logger_config import get_logger




























































"""
"""Core business logic and data management

This module provides timezone functionality including:
- 4 functions: __init__, now, to_timezone...
- 1 classes: TimezoneManager

Usage:
    # Example usage here
"""
Timezone-aware scheduling.
"""




logger = get_logger(__name__)


class TimezoneManager:
    """Timezone manager for timezone-aware scheduling."""

    def __init__(self, timezone: Optional[str] = None):
        """Initialize timezone manager.

        Args:
            timezone: Timezone name (e.g., "UTC", "America/New_York")
                     Default: UTC
        """
        self.timezone_str = timezone or "UTC"
        try:
            self.timezone = pytz.timezone(self.timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone {timezone}, using UTC")
            self.timezone = pytz.UTC
            self.timezone_str = "UTC"

    def now(self) -> datetime:
        """Get current datetime in configured timezone.

        Returns:
            Current datetime in configured timezone
        """
        return datetime.now(self.timezone)

    def to_timezone(self, dt: datetime, timezone: str) -> datetime:
        """Convert datetime to specified timezone.

        Args:
            dt: Datetime to convert
            timezone: Target timezone name

        Returns:
            Datetime in target timezone
        """
        try:
            target_tz = pytz.timezone(timezone)
            if dt.tzinfo is None:
                dt = pytz.UTC.localize(dt)
            return dt.astimezone(target_tz)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone {timezone}, returning original datetime")
            return dt

    def localize(self, dt: datetime) -> datetime:
        """Localize a naive datetime to configured timezone.

        Args:
            dt: Naive datetime

        Returns:
            Localized datetime
        """
        if dt.tzinfo is None:
            return self.timezone.localize(dt)
        return dt.astimezone(self.timezone)


