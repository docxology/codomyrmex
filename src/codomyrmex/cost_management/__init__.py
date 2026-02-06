"""
Cost Management Module

Spend tracking, budgeting, and cost optimization.
"""

__version__ = "0.1.0"

import json
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class CostCategory(Enum):
    """Categories of costs."""
    LLM_INFERENCE = "llm_inference"
    LLM_EMBEDDING = "llm_embedding"
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    API_CALLS = "api_calls"
    OTHER = "other"


class BudgetPeriod(Enum):
    """Budget periods."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class CostEntry:
    """A single cost entry."""
    id: str
    amount: float
    category: CostCategory
    description: str = ""
    resource_id: str = ""
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category.value,
            "description": self.description,
            "resource_id": self.resource_id,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Budget:
    """A budget allocation."""
    id: str
    name: str
    amount: float
    period: BudgetPeriod
    category: CostCategory | None = None
    tags_filter: dict[str, str] = field(default_factory=dict)
    alert_thresholds: list[float] = field(default_factory=lambda: [0.5, 0.8, 0.9, 1.0])

    def get_period_start(self, reference: datetime = None) -> datetime:
        """Get the start of the current budget period."""
        ref = reference or datetime.now()

        if self.period == BudgetPeriod.HOURLY:
            return ref.replace(minute=0, second=0, microsecond=0)
        elif self.period == BudgetPeriod.DAILY:
            return ref.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.period == BudgetPeriod.WEEKLY:
            start = ref - timedelta(days=ref.weekday())
            return start.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.period == BudgetPeriod.MONTHLY:
            return ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        return ref


@dataclass
class CostSummary:
    """Summary of costs."""
    total: float = 0.0
    by_category: dict[str, float] = field(default_factory=dict)
    by_resource: dict[str, float] = field(default_factory=dict)
    by_tag: dict[str, dict[str, float]] = field(default_factory=dict)
    entry_count: int = 0
    period_start: datetime | None = None
    period_end: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total": self.total,
            "by_category": self.by_category,
            "by_resource": self.by_resource,
            "entry_count": self.entry_count,
        }


@dataclass
class BudgetAlert:
    """A budget alert."""
    budget_id: str
    threshold: float
    current_spend: float
    budget_amount: float
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def utilization(self) -> float:
        """Get budget utilization percentage."""
        return self.current_spend / self.budget_amount if self.budget_amount > 0 else 0

    @property
    def message(self) -> str:
        """Get alert message."""
        pct = int(self.utilization * 100)
        return f"Budget '{self.budget_id}' at {pct}% utilization (${self.current_spend:.2f}/${self.budget_amount:.2f})"


class CostStore(ABC):
    """Base class for cost storage."""

    @abstractmethod
    def save_entry(self, entry: CostEntry) -> None:
        """Save a cost entry."""
        pass

    @abstractmethod
    def get_entries(
        self,
        start: datetime,
        end: datetime,
        category: CostCategory | None = None,
    ) -> list[CostEntry]:
        """Get entries in date range."""
        pass


class InMemoryCostStore(CostStore):
    """In-memory cost storage."""

    def __init__(self):
        self._entries: list[CostEntry] = []
        self._lock = threading.Lock()

    def save_entry(self, entry: CostEntry) -> None:
        """Save a cost entry."""
        with self._lock:
            self._entries.append(entry)

    def get_entries(
        self,
        start: datetime,
        end: datetime,
        category: CostCategory | None = None,
    ) -> list[CostEntry]:
        """Get entries in date range."""
        results = []
        for entry in self._entries:
            if start <= entry.timestamp <= end:
                if category is None or entry.category == category:
                    results.append(entry)
        return results

    def get_all(self) -> list[CostEntry]:
        """Get all entries."""
        return list(self._entries)

    def clear(self) -> None:
        """Clear all entries."""
        with self._lock:
            self._entries.clear()


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


__all__ = [
    # Enums
    "CostCategory",
    "BudgetPeriod",
    # Data classes
    "CostEntry",
    "Budget",
    "CostSummary",
    "BudgetAlert",
    # Stores
    "CostStore",
    "InMemoryCostStore",
    # Core
    "CostTracker",
    "BudgetManager",
]
