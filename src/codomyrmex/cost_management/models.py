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
