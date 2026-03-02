"""
Cost Management Tracker and Budget Manager

Cost tracking service and budget management with alerting.
"""

import threading
from datetime import datetime
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .models import (
    Budget,
    BudgetAlert,
    BudgetPeriod,
    CostCategory,
    CostEntry,
    CostSummary,
)
from .stores import CostStore, InMemoryCostStore

logger = get_logger(__name__)


class CostTracker:
    """
    Main cost tracking service.

    Usage:
        tracker = CostTracker()

        # Record costs
        tracker.record(
            amount=0.05,
            category=CostCategory.LLM_INFERENCE,
            description="GPT-4 completion",
            tags={"model": "gpt-4", "user": "alice"},
        )

        # Get summary
        summary = tracker.get_summary(period=BudgetPeriod.DAILY)
        print(f"Today's spend: ${summary.total:.2f}")
    """

    def __init__(self, store: CostStore | None = None) -> None:
        self.store = store or InMemoryCostStore()
        self._counter = 0
        self._lock = threading.Lock()

    def _generate_id(self) -> str:
        """Generate unique entry ID."""
        with self._lock:
            self._counter += 1
            return f"cost_{self._counter}_{int(datetime.now().timestamp())}"

    def record(
        self,
        amount: float,
        category: CostCategory = CostCategory.LLM_INFERENCE,
        description: str = "",
        resource_id: str = "",
        tags: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> CostEntry:
        """
        Record a cost entry.

        Args:
            amount: Cost amount in dollars
            category: Cost category
            description: Description of the cost
            resource_id: ID of the resource that incurred the cost
            tags: Key-value tags for filtering
            metadata: Additional metadata
            timestamp: Optional custom timestamp

        Returns:
            The created CostEntry
        """
        entry = CostEntry(
            id=self._generate_id(),
            amount=amount,
            category=category,
            description=description,
            resource_id=resource_id,
            tags=tags or {},
            metadata=metadata or {},
            timestamp=timestamp or datetime.now(),
        )

        self.store.save_entry(entry)
        logger.debug(
            f"Recorded cost: ${amount:.4f} for {category.value} ({description})"
        )
        return entry

    def get_summary(
        self,
        period: BudgetPeriod | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        category: CostCategory | None = None,
        tags_filter: dict[str, str] | None = None,
    ) -> CostSummary:
        """
        Get cost summary for a period.

        Args:
            period: Budget period (uses current period)
            start: Custom start date
            end: Custom end date
            category: Filter by category
            tags_filter: Filter by tags

        Returns:
            CostSummary with aggregated costs
        """
        if start is None:
            if period:
                budget = Budget(id="temp", name="temp", amount=0, period=period)
                start = budget.get_period_start()
            else:
                start = datetime.min

        if end is None:
            end = datetime.now()

        entries = self.store.get_entries(
            start=start, end=end, category=category, tags_filter=tags_filter
        )

        summary = CostSummary(
            entry_count=len(entries),
            period_start=start,
            period_end=end,
        )

        for entry in entries:
            summary.total += entry.amount

            # By category
            cat = entry.category.value
            summary.by_category[cat] = summary.by_category.get(cat, 0.0) + entry.amount

            # By resource
            if entry.resource_id:
                summary.by_resource[entry.resource_id] = (
                    summary.by_resource.get(entry.resource_id, 0.0) + entry.amount
                )

            # By tag
            for tag_key, tag_value in entry.tags.items():
                if tag_key not in summary.by_tag:
                    summary.by_tag[tag_key] = {}
                summary.by_tag[tag_key][tag_value] = (
                    summary.by_tag[tag_key].get(tag_value, 0.0) + entry.amount
                )

        return summary

    def get_total(
        self,
        period: BudgetPeriod | None = None,
        category: CostCategory | None = None,
        tags_filter: dict[str, str] | None = None,
    ) -> float:
        """Get total cost for period and optional filters."""
        summary = self.get_summary(
            period=period, category=category, tags_filter=tags_filter
        )
        return summary.total


class BudgetManager:
    """
    Budget management and alerting.

    Usage:
        budgets = BudgetManager(tracker)

        # Create budget
        budgets.create(
            name="Daily LLM",
            amount=100.0,
            period=BudgetPeriod.DAILY,
            category=CostCategory.LLM_INFERENCE,
        )

        # Check budgets
        alerts = budgets.check_budgets()
        for alert in alerts:
            print(alert.message)
    """

    def __init__(self, tracker: CostTracker) -> None:
        self.tracker = tracker
        self._budgets: dict[str, Budget] = {}
        self._triggered_alerts: set[str] = set()  # Track which thresholds were triggered
        self._lock = threading.Lock()

    def create(
        self,
        name: str,
        amount: float,
        period: BudgetPeriod,
        category: CostCategory | None = None,
        tags_filter: dict[str, str] | None = None,
        alert_thresholds: list[float] | None = None,
    ) -> Budget:
        """Create a budget."""
        budget_id = name.lower().replace(" ", "_")
        budget = Budget(
            id=budget_id,
            name=name,
            amount=amount,
            period=period,
            category=category,
            tags_filter=tags_filter or {},
            alert_thresholds=alert_thresholds or [0.5, 0.8, 0.9, 1.0],
        )

        with self._lock:
            self._budgets[budget.id] = budget

        logger.info(f"Created budget: {name} (${amount:.2f} per {period.value})")
        return budget

    def get_budget(self, budget_id: str) -> Budget | None:
        """Get budget by ID."""
        return self._budgets.get(budget_id)

    def list_budgets(self) -> list[Budget]:
        """List all budgets."""
        return list(self._budgets.values())

    def get_utilization(self, budget: Budget) -> float:
        """Get current budget utilization."""
        start = budget.get_period_start()
        summary = self.tracker.get_summary(
            start=start, category=budget.category, tags_filter=budget.tags_filter
        )

        return summary.total / budget.amount if budget.amount > 0 else 0

    def check_budgets(self) -> list[BudgetAlert]:
        """Check all budgets and return new alerts."""
        alerts = []

        for budget in self._budgets.values():
            start = budget.get_period_start()
            summary = self.tracker.get_summary(
                start=start, category=budget.category, tags_filter=budget.tags_filter
            )

            utilization = summary.total / budget.amount if budget.amount > 0 else 0

            for threshold in budget.alert_thresholds:
                alert_key = f"{budget.id}_{threshold}"

                if utilization >= threshold and alert_key not in self._triggered_alerts:
                    alert = BudgetAlert(
                        budget_id=budget.id,
                        threshold=threshold,
                        current_spend=summary.total,
                        budget_amount=budget.amount,
                    )
                    alerts.append(alert)
                    self._triggered_alerts.add(alert_key)
                    logger.warning(alert.message)

        return alerts

    def reset_period_alerts(self) -> None:
        """Reset triggered alerts (call at period boundary)."""
        with self._lock:
            self._triggered_alerts.clear()
            logger.debug("Budget alerts reset.")

    def can_spend(
        self, amount: float, category: CostCategory, tags: dict[str, str] | None = None
    ) -> bool:
        """Check if spending amount is within all applicable budgets."""
        tags = tags or {}

        for budget in self._budgets.values():
            # Check if this budget applies to this spend
            if budget.category and budget.category != category:
                continue

            match = True
            for k, v in budget.tags_filter.items():
                if tags.get(k) != v:
                    match = False
                    break
            if not match:
                continue

            # Check utilization
            utilization = self.get_utilization(budget)
            remaining = budget.amount * (1 - utilization)
            if amount > remaining:
                logger.warning(
                    f"Spend blocked by budget '{budget.id}': "
                    f"Need ${amount:.4f}, only ${remaining:.4f} remaining."
                )
                return False

        return True
