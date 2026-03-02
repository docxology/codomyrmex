"""
SLO/SLI Tracking

Service Level Objectives and Indicators for observability.
"""

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SLIType(Enum):
    """Service Level Indicator types."""
    AVAILABILITY = "availability"  # Uptime percentage
    LATENCY = "latency"  # Response time
    THROUGHPUT = "throughput"  # Requests per second
    ERROR_RATE = "error_rate"  # Error percentage
    SATURATION = "saturation"  # Resource utilization


@dataclass
class SLI:
    """A Service Level Indicator."""
    name: str
    sli_type: SLIType
    good_events: int = 0
    total_events: int = 0
    description: str = ""

    @property
    def value(self) -> float:
        """Calculate SLI value as a percentage."""
        if self.total_events == 0:
            return 100.0
        return (self.good_events / self.total_events) * 100

    def record_good(self, count: int = 1) -> None:
        """Record good events."""
        self.good_events += count
        self.total_events += count

    def record_bad(self, count: int = 1) -> None:
        """Record bad events."""
        self.total_events += count


@dataclass
class SLO:
    """A Service Level Objective."""
    id: str
    name: str
    sli: SLI
    target: float  # Target percentage (e.g., 99.9)
    window_days: int = 30  # Measurement window
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_met(self) -> bool:
        """Check if SLO is currently being met."""
        return self.sli.value >= self.target

    @property
    def error_budget_remaining(self) -> float:
        """Calculate remaining error budget as percentage."""
        allowed_failures = 100.0 - self.target  # e.g., 0.1% for 99.9%
        actual_failures = 100.0 - self.sli.value
        if allowed_failures == 0:
            return 0.0 if actual_failures > 0 else 100.0
        remaining = ((allowed_failures - actual_failures) / allowed_failures) * 100
        return max(0.0, min(100.0, remaining))

    @property
    def error_budget_consumed(self) -> float:
        """Calculate consumed error budget as percentage."""
        return 100.0 - self.error_budget_remaining


@dataclass
class SLOViolation:
    """An SLO violation event."""
    slo_id: str
    slo_name: str
    target: float
    actual: float
    occurred_at: datetime = field(default_factory=datetime.now)
    duration_minutes: float = 0.0


class SLOTracker:
    """Track SLOs and error budgets."""

    def __init__(self):
        self._slos: dict[str, SLO] = {}
        self._violations: list[SLOViolation] = []
        self._lock = threading.Lock()

    def create_slo(
        self,
        slo_id: str,
        name: str,
        sli_type: SLIType,
        target: float,
        window_days: int = 30,
        description: str = "",
    ) -> SLO:
        """Create a new SLO."""
        sli = SLI(
            name=f"{name}_sli",
            sli_type=sli_type,
            description=f"SLI for {name}",
        )
        slo = SLO(
            id=slo_id,
            name=name,
            sli=sli,
            target=target,
            window_days=window_days,
            description=description,
        )
        with self._lock:
            self._slos[slo_id] = slo
        return slo

    def get_slo(self, slo_id: str) -> SLO | None:
        """Get an SLO by ID."""
        return self._slos.get(slo_id)

    def record_event(
        self,
        slo_id: str,
        is_good: bool,
        count: int = 1,
    ) -> None:
        """Record an event for an SLO."""
        slo = self._slos.get(slo_id)
        if not slo:
            return

        with self._lock:
            if is_good:
                slo.sli.record_good(count)
            else:
                slo.sli.record_bad(count)

            # Check for violation
            if not slo.is_met:
                self._violations.append(SLOViolation(
                    slo_id=slo.id,
                    slo_name=slo.name,
                    target=slo.target,
                    actual=slo.sli.value,
                ))

    def get_status(self, slo_id: str) -> dict[str, Any] | None:
        """Get SLO status."""
        slo = self._slos.get(slo_id)
        if not slo:
            return None

        return {
            "id": slo.id,
            "name": slo.name,
            "target": slo.target,
            "current": slo.sli.value,
            "is_met": slo.is_met,
            "error_budget_remaining": slo.error_budget_remaining,
            "error_budget_consumed": slo.error_budget_consumed,
            "good_events": slo.sli.good_events,
            "total_events": slo.sli.total_events,
        }

    def get_all_status(self) -> list[dict[str, Any]]:
        """Get status for all SLOs."""
        return [
            self.get_status(slo_id)
            for slo_id in self._slos
            if self.get_status(slo_id) is not None
        ]

    def get_violations(
        self,
        slo_id: str | None = None,
        since: datetime | None = None,
    ) -> list[SLOViolation]:
        """Get SLO violations."""
        violations = self._violations

        if slo_id:
            violations = [v for v in violations if v.slo_id == slo_id]

        if since:
            violations = [v for v in violations if v.occurred_at >= since]

        return violations


class ErrorBudgetPolicy:
    """Policies based on error budget consumption."""

    def __init__(self, tracker: SLOTracker):
        self.tracker = tracker
        self._policies: dict[str, Callable[[float], None]] = {}

    def add_policy(
        self,
        name: str,
        action: Callable[[float], None],
    ) -> None:
        """Add a policy action."""
        self._policies[name] = action

    def evaluate(self, slo_id: str) -> str | None:
        """Evaluate policies for an SLO."""
        status = self.tracker.get_status(slo_id)
        if not status:
            return None

        consumed = status["error_budget_consumed"]

        # Default thresholds
        if consumed >= 100:
            return "freeze_deployments"
        elif consumed >= 75:
            return "reduce_risk"
        elif consumed >= 50:
            return "increase_reviews"

        return "normal"


__all__ = [
    "SLI",
    "SLIType",
    "SLO",
    "SLOViolation",
    "SLOTracker",
    "ErrorBudgetPolicy",
]
