"""
Cost Management Models

Data classes and enums for cost tracking and budgeting.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class CostCategory(Enum):
    """Categories of costs."""

    LLM_INFERENCE = "llm_inference"
    LLM_EMBEDDING = "llm_embedding"
    LLM_FINE_TUNING = "llm_fine_tuning"
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    API_CALLS = "api_calls"
    DATABASE = "database"
    LICENSE = "license"
    OTHER = "other"


class BudgetPeriod(Enum):
    """Budget periods."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


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
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CostEntry":
        """Create from dictionary."""
        data_copy = data.copy()
        data_copy["category"] = CostCategory(data_copy["category"])
        if isinstance(data_copy["timestamp"], str):
            data_copy["timestamp"] = datetime.fromisoformat(data_copy["timestamp"])
        return cls(**data_copy)


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

    def get_period_start(self, reference: datetime | None = None) -> datetime:
        """Get the start of the current budget period."""
        ref = reference or datetime.now()

        if self.period == BudgetPeriod.HOURLY:
            return ref.replace(minute=0, second=0, microsecond=0)
        if self.period == BudgetPeriod.DAILY:
            return ref.replace(hour=0, minute=0, second=0, microsecond=0)
        if self.period == BudgetPeriod.WEEKLY:
            start = ref - timedelta(days=ref.weekday())
            return start.replace(hour=0, minute=0, second=0, microsecond=0)
        if self.period == BudgetPeriod.MONTHLY:
            return ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if self.period == BudgetPeriod.YEARLY:
            return ref.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )

        return ref

    def is_match(self, entry: CostEntry) -> bool:
        """Check if a cost entry matches this budget's filters."""
        if self.category and entry.category != self.category:
            return False

        for key, value in self.tags_filter.items():
            if entry.tags.get(key) != value:
                return False

        return True


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
            "by_tag": self.by_tag,
            "entry_count": self.entry_count,
            "period_start": self.period_start.isoformat()
            if self.period_start
            else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
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
