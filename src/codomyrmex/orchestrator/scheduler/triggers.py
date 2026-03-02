"""
Scheduler Triggers

Trigger types for job scheduling: once, interval, and cron.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class TriggerType(Enum):
    """Types of job triggers."""
    ONCE = "once"
    INTERVAL = "interval"
    CRON = "cron"


@dataclass
class Trigger(ABC):
    """Base class for job triggers."""

    @abstractmethod
    def get_next_run(self, from_time: datetime | None = None) -> datetime | None:
        """Get the next run time."""
        pass

    @abstractmethod
    def get_type(self) -> TriggerType:
        """Get trigger type."""
        pass


@dataclass
class OnceTrigger(Trigger):
    """Trigger that fires once at a specific time."""
    run_at: datetime

    def get_next_run(self, from_time: datetime | None = None) -> datetime | None:
        """get Next Run ."""
        from_time = from_time or datetime.now()
        if self.run_at > from_time:
            return self.run_at
        return None

    def get_type(self) -> TriggerType:
        """get Type ."""
        return TriggerType.ONCE


@dataclass
class IntervalTrigger(Trigger):
    """Trigger that fires at regular intervals."""
    seconds: int = 0
    minutes: int = 0
    hours: int = 0
    days: int = 0
    start_time: datetime | None = None
    end_time: datetime | None = None

    @property
    def interval_seconds(self) -> int:
        """interval Seconds ."""
        return (
            self.seconds +
            self.minutes * 60 +
            self.hours * 3600 +
            self.days * 86400
        )

    def get_next_run(self, from_time: datetime | None = None) -> datetime | None:
        """get Next Run ."""
        from_time = from_time or datetime.now()
        start = self.start_time or datetime.now()

        if from_time < start:
            return start

        elapsed = (from_time - start).total_seconds()
        intervals_passed = int(elapsed / self.interval_seconds) + 1
        next_run = start + timedelta(seconds=intervals_passed * self.interval_seconds)

        if self.end_time and next_run > self.end_time:
            return None

        return next_run

    def get_type(self) -> TriggerType:
        """get Type ."""
        return TriggerType.INTERVAL


@dataclass
class CronTrigger(Trigger):
    """Cron-style trigger (simplified)."""
    minute: str = "*"
    hour: str = "*"
    day_of_month: str = "*"
    month: str = "*"
    day_of_week: str = "*"

    def _match_field(self, field_pattern: str, value: int, max_val: int) -> bool:
        """Check if value matches cron pattern."""
        if field_pattern == "*":
            return True

        # Handle comma-separated values
        for part in field_pattern.split(","):
            # Handle ranges
            if "-" in part:
                low, high = map(int, part.split("-"))
                if low <= value <= high:
                    return True
            # Handle step values
            elif "/" in part:
                base, step = part.split("/")
                step = int(step)
                if base == "*":
                    if value % step == 0:
                        return True
            else:
                if int(part) == value:
                    return True

        return False

    def get_next_run(self, from_time: datetime | None = None) -> datetime | None:
        """Get next run time (simplified implementation)."""
        from_time = from_time or datetime.now()
        candidate = from_time.replace(second=0, microsecond=0) + timedelta(minutes=1)

        # Search up to 1 year ahead
        max_iterations = 525600  # minutes in a year

        for _ in range(max_iterations):
            if (
                self._match_field(self.minute, candidate.minute, 59) and
                self._match_field(self.hour, candidate.hour, 23) and
                self._match_field(self.day_of_month, candidate.day, 31) and
                self._match_field(self.month, candidate.month, 12) and
                self._match_field(self.day_of_week, candidate.weekday(), 6)
            ):
                return candidate
            candidate += timedelta(minutes=1)

        return None

    def get_type(self) -> TriggerType:
        """get Type ."""
        return TriggerType.CRON

    @classmethod
    def from_expression(cls, expr: str) -> "CronTrigger":
        """Parse cron expression (minute hour day month weekday)."""
        parts = expr.strip().split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {expr}")

        return cls(
            minute=parts[0],
            hour=parts[1],
            day_of_month=parts[2],
            month=parts[3],
            day_of_week=parts[4],
        )
