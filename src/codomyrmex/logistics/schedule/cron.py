"""
Cron-like scheduling with pattern parsing.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

from .timezone import TimezoneManager

logger = get_logger(__name__)


@dataclass
class CronExpression:
    """Cron expression parser and evaluator."""

    minute: List[int]
    hour: List[int]
    day_of_month: List[int]
    month: List[int]
    day_of_week: List[int]

    @classmethod
    def parse(cls, expression: str) -> "CronExpression":
        """Parse a cron expression.

        Args:
            expression: Cron expression (e.g., "0 0 * * *")

        Returns:
            CronExpression instance

        Raises:
            ValueError: If expression is invalid
        """
        parts = expression.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {expression}")

        return cls(
            minute=cls._parse_field(parts[0], 0, 59),
            hour=cls._parse_field(parts[1], 0, 23),
            day_of_month=cls._parse_field(parts[2], 1, 31),
            month=cls._parse_field(parts[3], 1, 12),
            day_of_week=cls._parse_field(parts[4], 0, 6),
        )

    @staticmethod
    def _parse_field(field: str, min_val: int, max_val: int) -> List[int]:
        """Parse a cron field.

        Args:
            field: Field value (e.g., "*", "5", "1-5", "*/2")
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            List of valid values
        """
        if field == "*":
            return list(range(min_val, max_val + 1))

        values = []
        for part in field.split(","):
            if "/" in part:
                step_part, step = part.split("/")
                step = int(step)
                if step_part == "*":
                    values.extend(range(min_val, max_val + 1, step))
                else:
                    start = int(step_part) if step_part else min_val
                    values.extend(range(start, max_val + 1, step))
            elif "-" in part:
                start, end = map(int, part.split("-"))
                values.extend(range(start, end + 1))
            else:
                values.append(int(part))

        return sorted(set(values))

    def matches(self, dt: datetime) -> bool:
        """Check if a datetime matches this cron expression.

        Args:
            dt: Datetime to check

        Returns:
            True if matches, False otherwise
        """
        return (
            dt.minute in self.minute
            and dt.hour in self.hour
            and dt.day in self.day_of_month
            and dt.month in self.month
            and dt.weekday() in self.day_of_week
        )


class CronScheduler:
    """Cron scheduler for evaluating cron expressions."""

    def __init__(self, timezone_manager: TimezoneManager):
        """Initialize cron scheduler.

        Args:
            timezone_manager: TimezoneManager instance
        """
        self.timezone_manager = timezone_manager

    def should_run(self, cron: CronExpression, now: Optional[datetime] = None) -> bool:
        """Check if a cron expression should run now.

        Args:
            cron: CronExpression instance
            now: Current datetime (default: timezone_manager.now())

        Returns:
            True if should run, False otherwise
        """
        if now is None:
            now = self.timezone_manager.now()
        return cron.matches(now)


