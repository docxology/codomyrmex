"""Cost management data models.

defines the core data structures used by the cost tracking
and budget management subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class CostCategory(Enum):
    """Categories of cost entries."""

    LLM_INFERENCE = "llm_inference"
    EMBEDDING = "embedding"
    STORAGE = "storage"
    COMPUTE = "compute"
    NETWORK = "network"
    API_CALL = "api_call"
    AUDIO = "audio"
    VISION = "vision"
    OTHER = "other"


class BudgetPeriod(Enum):
    """Budget period granularities."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class CostEntry:
    """A single cost event.

    Attributes:
        id: Unique identifier.
        amount: Cost in USD.
        category: Cost category.
        description: Human-readable description.
        resource_id: ID of the resource that incurred the cost.
        timestamp: When the cost was recorded.
        tags: Key-value tags for filtering.
        metadata: Additional metadata.
    """

    id: str
    amount: float
    category: CostCategory = CostCategory.LLM_INFERENCE
    description: str = ""
    resource_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CostSummary:
    """Aggregated cost summary for a period.

    Attributes:
        total: Total cost in USD.
        entry_count: Number of cost entries.
        period_start: Start of period.
        period_end: End of period.
        by_category: Cost breakdown by category.
        by_resource: Cost breakdown by resource.
        by_tag: Cost breakdown by tag key/value.
        entries: The raw entries in this period.
    """

    total: float = 0.0
    entry_count: int = 0
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    by_category: dict[str, float] = field(default_factory=dict)
    by_resource: dict[str, float] = field(default_factory=dict)
    by_tag: dict[str, dict[str, float]] = field(default_factory=dict)
    entries: list[CostEntry] = field(default_factory=list)


@dataclass
class Budget:
    """A budget definition.

    Attributes:
        id: Unique identifier.
        name: Human-readable name.
        amount: Budget limit in USD.
        period: Budget period.
        category: Optional category filter.
        tags_filter: Optional tag filter.
        alert_thresholds: Utilization thresholds that trigger alerts.
    """

    id: str
    name: str
    amount: float
    period: BudgetPeriod
    category: CostCategory | None = None
    tags_filter: dict[str, str] = field(default_factory=dict)
    alert_thresholds: list[float] = field(default_factory=lambda: [0.5, 0.8, 0.9, 1.0])

    def get_period_start(self) -> datetime:
        """Calculate the start of the current period."""
        now = datetime.now()
        if self.period == BudgetPeriod.HOURLY:
            return now.replace(minute=0, second=0, microsecond=0)
        if self.period == BudgetPeriod.DAILY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        if self.period == BudgetPeriod.WEEKLY:
            start = now - timedelta(days=now.weekday())
            return start.replace(hour=0, minute=0, second=0, microsecond=0)
        if self.period == BudgetPeriod.MONTHLY:
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return now


@dataclass
class BudgetAlert:
    """An alert triggered when a budget threshold is crossed.

    Attributes:
        budget_id: ID of the budget.
        threshold: The threshold that was crossed (0.0–1.0).
        current_spend: Current spending amount in USD.
        budget_amount: The budget limit in USD.
        timestamp: When the alert was triggered.
    """

    budget_id: str
    threshold: float
    current_spend: float
    budget_amount: float
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def utilization(self) -> float:
        """Current utilization ratio."""
        return self.current_spend / self.budget_amount if self.budget_amount > 0 else 0

    @property
    def message(self) -> str:
        """Human-readable alert message."""
        pct = self.threshold * 100
        return (
            f"Budget '{self.budget_id}' has reached {pct:.0f}% utilization "
            f"(${self.current_spend:.2f}/${self.budget_amount:.2f})"
        )


__all__ = [
    "Budget",
    "BudgetAlert",
    "BudgetPeriod",
    "CostCategory",
    "CostEntry",
    "CostSummary",
]
