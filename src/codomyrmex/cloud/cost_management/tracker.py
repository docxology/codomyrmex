"""
Cost Management Tracker and Budget Manager

Cost tracking service and budget management with alerting.
"""

import threading
from datetime import datetime
from typing import Any

from .models import (
    Budget,
    BudgetAlert,
    BudgetPeriod,
    CostCategory,
    CostEntry,
    CostSummary,
)
from .stores import CostStore, InMemoryCostStore


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

    def __init__(self, store: CostStore | None = None):
        """Initialize this instance."""
        self.store = store or InMemoryCostStore()
        self._counter = 0
        self._lock = threading.Lock()

    def _generate_id(self) -> str:
        """Generate unique entry ID."""
        with self._lock:
            self._counter += 1
            return f"cost_{self._counter}"

    def record(
        self,
        amount: float,
        category: CostCategory = CostCategory.LLM_INFERENCE,
        description: str = "",
        resource_id: str = "",
        tags: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
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
        )

        self.store.save_entry(entry)
        return entry

    def get_summary(
        self,
        period: BudgetPeriod | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> CostSummary:
        """
        Get cost summary for a period.

        Args:
            period: Budget period (uses current period)
            start: Custom start date
            end: Custom end date

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

        entries = self.store.get_entries(start, end)

        summary = CostSummary(
            entry_count=len(entries),
            period_start=start,
            period_end=end,
        )

        for entry in entries:
            summary.total += entry.amount

            # By category
            cat = entry.category.value
            summary.by_category[cat] = summary.by_category.get(cat, 0) + entry.amount

            # By resource
            if entry.resource_id:
                summary.by_resource[entry.resource_id] = (
                    summary.by_resource.get(entry.resource_id, 0) + entry.amount
                )

            # By tag
            for tag_key, tag_value in entry.tags.items():
                if tag_key not in summary.by_tag:
                    summary.by_tag[tag_key] = {}
                summary.by_tag[tag_key][tag_value] = (
                    summary.by_tag[tag_key].get(tag_value, 0) + entry.amount
                )

        return summary

    def get_total(
        self,
        period: BudgetPeriod | None = None,
        category: CostCategory | None = None,
    ) -> float:
        """Get total cost for period and optional category."""
        summary = self.get_summary(period=period)

        if category:
            return summary.by_category.get(category.value, 0)

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

    def __init__(self, tracker: CostTracker):
        """Initialize this instance."""
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
        budget = Budget(
            id=name.lower().replace(" ", "_"),
            name=name,
            amount=amount,
            period=period,
            category=category,
            tags_filter=tags_filter or {},
            alert_thresholds=alert_thresholds or [0.5, 0.8, 0.9, 1.0],
        )

        with self._lock:
            self._budgets[budget.id] = budget

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
        summary = self.tracker.get_summary(start=start)

        # Filter by category if specified
        if budget.category:
            spend = summary.by_category.get(budget.category.value, 0)
        else:
            spend = summary.total

        return spend / budget.amount if budget.amount > 0 else 0

    def check_budgets(self) -> list[BudgetAlert]:
        """Check all budgets and return new alerts."""
        alerts = []

        for budget in self._budgets.values():
            start = budget.get_period_start()
            summary = self.tracker.get_summary(start=start)

            if budget.category:
                spend = summary.by_category.get(budget.category.value, 0)
            else:
                spend = summary.total

            utilization = spend / budget.amount if budget.amount > 0 else 0

            for threshold in budget.alert_thresholds:
                alert_key = f"{budget.id}_{threshold}"

                if utilization >= threshold and alert_key not in self._triggered_alerts:
                    alerts.append(BudgetAlert(
                        budget_id=budget.id,
                        threshold=threshold,
                        current_spend=spend,
                        budget_amount=budget.amount,
                    ))
                    self._triggered_alerts.add(alert_key)

        return alerts

    def reset_period_alerts(self) -> None:
        """Reset triggered alerts (call at period boundary)."""
        with self._lock:
            self._triggered_alerts.clear()

    def can_spend(self, amount: float, budget_id: str | None = None) -> bool:
        """Check if spending amount is within budget."""
        if budget_id:
            budget = self.get_budget(budget_id)
            if not budget:
                return True

            utilization = self.get_utilization(budget)
            remaining = budget.amount * (1 - utilization)
            return amount <= remaining

        # Check all budgets
        for budget in self._budgets.values():
            utilization = self.get_utilization(budget)
            remaining = budget.amount * (1 - utilization)
            if amount > remaining:
                return False

        return True
