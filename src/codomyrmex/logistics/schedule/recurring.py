"""
Recurring schedule definitions (daily, weekly, monthly, etc.).
"""

from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum

from codomyrmex.logging_monitoring.logger_config import get_logger

from .timezone import TimezoneManager

logger = get_logger(__name__)


class RecurrenceType(Enum):
    """Recurrence type enumeration."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class RecurringSchedule:
    """Recurring schedule definition."""

    recurrence_type: RecurrenceType
    time: time
    day_of_week: int | None = None  # 0-6, Monday=0
    day_of_month: int | None = None  # 1-31
    month: int | None = None  # 1-12
    last_run: datetime | None = None

    def __post_init__(self):
        """Validate schedule configuration."""
        if self.recurrence_type == RecurrenceType.WEEKLY and self.day_of_week is None:
            raise ValueError("day_of_week required for weekly recurrence")
        if self.recurrence_type == RecurrenceType.MONTHLY and self.day_of_month is None:
            raise ValueError("day_of_month required for monthly recurrence")
        if self.recurrence_type == RecurrenceType.YEARLY:
            if self.day_of_month is None or self.month is None:
                raise ValueError("day_of_month and month required for yearly recurrence")


class RecurringScheduler:
    """Recurring scheduler for evaluating recurring schedules."""

    def __init__(self, timezone_manager: TimezoneManager):
        """Initialize recurring scheduler.

        Args:
            timezone_manager: TimezoneManager instance
        """
        self.timezone_manager = timezone_manager

    def should_run(
        self, schedule: RecurringSchedule, now: datetime | None = None
    ) -> bool:
        """Check if a recurring schedule should run now.

        Args:
            schedule: RecurringSchedule instance
            now: Current datetime (default: timezone_manager.now())

        Returns:
            True if should run, False otherwise
        """
        if now is None:
            now = self.timezone_manager.now()

        # Check if time matches
        if now.time() < schedule.time:
            return False

        # Check if already ran today
        if schedule.last_run and schedule.last_run.date() == now.date():
            return False

        # Check recurrence type
        if schedule.recurrence_type == RecurrenceType.DAILY:
            return now.time() >= schedule.time

        elif schedule.recurrence_type == RecurrenceType.WEEKLY:
            return (
                now.weekday() == schedule.day_of_week
                and now.time() >= schedule.time
            )

        elif schedule.recurrence_type == RecurrenceType.MONTHLY:
            return (
                now.day == schedule.day_of_month
                and now.time() >= schedule.time
            )

        elif schedule.recurrence_type == RecurrenceType.YEARLY:
            return (
                now.month == schedule.month
                and now.day == schedule.day_of_month
                and now.time() >= schedule.time
            )

        return False


