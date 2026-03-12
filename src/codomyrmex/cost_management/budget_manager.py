"""Dynamic budget management subsystem.

Provides real-time budget enforcement with automatic pause at configurable
thresholds. Integrates with cost tracking to prevent overspend.

Example::

    budget = BudgetManager(daily_limit=10.0)
    budget.record_spend("gpt-4o", 0.05)
    assert budget.can_spend(0.01)  # True if under budget
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SpendRecord:
    """A single spend event.

    Attributes:
        model: Model or service name.
        amount: Amount spent (USD).
        timestamp: Unix timestamp.
        metadata: Additional context.
    """

    model: str
    amount: float
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BudgetAlert:
    """A budget threshold alert.

    Attributes:
        level: Alert level (``"warning"``, ``"critical"``, ``"paused"``).
        threshold: Utilization threshold that was breached.
        current_utilization: Current utilization ratio (0.0–1.0).
        message: Human-readable alert message.
        timestamp: When the alert was triggered.
    """

    level: str
    threshold: float
    current_utilization: float
    message: str
    timestamp: float = field(default_factory=time.time)


class BudgetManager:
    """Real-time budget enforcement with automatic pause.

    Args:
        daily_limit: Maximum daily spend in USD.
        warning_threshold: Utilization ratio for warning (default: 0.80).
        pause_threshold: Utilization ratio for auto-pause (default: 0.90).

    Example::

        mgr = BudgetManager(daily_limit=50.0)
        mgr.record_spend("gpt-4o", 2.50)
        if mgr.can_spend(1.00):
            # Proceed with API call
            mgr.record_spend("gpt-4o", 1.00)
    """

    def __init__(
        self,
        daily_limit: float = 100.0,
        warning_threshold: float = 0.80,
        pause_threshold: float = 0.90,
    ) -> None:
        self._daily_limit = daily_limit
        self._warning = warning_threshold
        self._pause = pause_threshold
        self._lock = threading.RLock()
        self._records: list[SpendRecord] = []
        self._alerts: list[BudgetAlert] = []
        self._paused = False
        self._webhooks: list[str] = []

    def record_spend(
        self,
        model: str,
        amount: float,
        metadata: dict[str, Any] | None = None,
    ) -> SpendRecord:
        """Record a spend event and check thresholds.

        Args:
            model: Model or service that incurred the cost.
            amount: Amount in USD.
            metadata: Optional context.

        Returns:
            The recorded :class:`SpendRecord`.
        """
        record = SpendRecord(model=model, amount=amount, metadata=metadata or {})
        with self._lock:
            self._records.append(record)
            self._check_thresholds()
        return record

    def can_spend(self, amount: float = 0.0) -> bool:
        """Check if spending is allowed.

        Args:
            amount: Proposed spend amount.

        Returns:
            ``True`` if daily spend + amount is under pause threshold.
        """
        if self._paused:
            return False
        current = self.get_daily_spend()
        return (current + amount) <= (self._daily_limit * self._pause)

    def get_daily_spend(self) -> float:
        """Get total spend for today.

        Returns:
            Total spend in USD for the current day.
        """
        today_start = _start_of_day()
        with self._lock:
            return sum(
                r.amount for r in self._records
                if r.timestamp >= today_start
            )

    def get_utilization(self) -> float:
        """Get current budget utilization ratio.

        Returns:
            Ratio of daily spend to daily limit (0.0–1.0+).
        """
        if self._daily_limit <= 0:
            return 0.0
        return self.get_daily_spend() / self._daily_limit

    def _check_thresholds(self) -> None:
        """Check and emit alerts for threshold breaches."""
        util = self.get_utilization()

        if util >= self._pause and not self._paused:
            self._paused = True
            alert = BudgetAlert(
                level="paused",
                threshold=self._pause,
                current_utilization=util,
                message=f"Budget paused: {util:.0%} of ${self._daily_limit:.2f} daily limit used",
            )
            self._alerts.append(alert)
            logger.warning(alert.message)
        elif util >= self._warning:
            alert = BudgetAlert(
                level="warning",
                threshold=self._warning,
                current_utilization=util,
                message=f"Budget warning: {util:.0%} of ${self._daily_limit:.2f} daily limit used",
            )
            self._alerts.append(alert)
            logger.warning(alert.message)

    def get_spend_by_model(self) -> dict[str, float]:
        """Get spend breakdown by model.

        Returns:
            Dict mapping model names to total spend.
        """
        today = _start_of_day()
        breakdown: dict[str, float] = defaultdict(float)
        with self._lock:
            for r in self._records:
                if r.timestamp >= today:
                    breakdown[r.model] += r.amount
        return dict(breakdown)

    def get_alerts(self) -> list[BudgetAlert]:
        """Get all budget alerts."""
        return list(self._alerts)

    def get_summary(self) -> dict[str, Any]:
        """Return a budget summary.

        Returns:
            Dict with ``daily_limit``, ``daily_spend``, ``utilization``, etc.
        """
        return {
            "daily_limit": self._daily_limit,
            "daily_spend": round(self.get_daily_spend(), 4),
            "utilization": round(self.get_utilization(), 4),
            "paused": self._paused,
            "alert_count": len(self._alerts),
            "spend_by_model": self.get_spend_by_model(),
        }

    def reset_daily(self) -> None:
        """Reset daily spend tracking."""
        with self._lock:
            today = _start_of_day()
            self._records = [r for r in self._records if r.timestamp < today]
            self._paused = False

    def register_webhook(self, url: str) -> None:
        """Register a webhook URL for budget alerts.

        Args:
            url: Webhook endpoint URL.
        """
        self._webhooks.append(url)

    @property
    def is_paused(self) -> bool:
        """Whether spending is currently paused."""
        return self._paused


def _start_of_day() -> float:
    """Get Unix timestamp for the start of today."""
    import datetime

    now = datetime.datetime.now(tz=datetime.UTC)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start.timestamp()


_singleton: BudgetManager | None = None


def get_budget_manager() -> BudgetManager:
    """Get the global budget manager singleton."""
    global _singleton
    if _singleton is None:
        _singleton = BudgetManager()
    return _singleton


__all__ = [
    "BudgetAlert",
    "BudgetManager",
    "SpendRecord",
    "get_budget_manager",
]
