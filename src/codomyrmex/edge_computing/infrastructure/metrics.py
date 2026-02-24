"""Edge computing invocation metrics and tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class InvocationRecord:
    """Record of a single function invocation."""

    function_id: str
    node_id: str
    duration_ms: float
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    error: str = ""


class EdgeMetrics:
    """Track metrics for edge function invocations."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self._records: list[InvocationRecord] = []

    def record(self, record: InvocationRecord) -> None:
        """Add an invocation record."""
        self._records.append(record)

    def total_invocations(
        self, function_id: str = None, node_id: str = None
    ) -> int:
        """Count invocations, optionally filtered."""
        records = self._records
        if function_id is not None:
            records = [r for r in records if r.function_id == function_id]
        if node_id is not None:
            records = [r for r in records if r.node_id == node_id]
        return len(records)

    def success_rate(self, function_id: str = None) -> float:
        """Success rate as percentage (0-100). Returns 100.0 if no records."""
        records = self._records
        if function_id is not None:
            records = [r for r in records if r.function_id == function_id]
        if not records:
            return 100.0
        successes = sum(1 for r in records if r.success)
        return (successes / len(records)) * 100.0

    def avg_latency_ms(self, function_id: str = None) -> float:
        """Average latency in ms. Returns 0.0 if no records."""
        records = self._records
        if function_id is not None:
            records = [r for r in records if r.function_id == function_id]
        if not records:
            return 0.0
        return sum(r.duration_ms for r in records) / len(records)

    def error_count(self, node_id: str = None) -> int:
        """Count of failed invocations."""
        records = self._records
        if node_id is not None:
            records = [r for r in records if r.node_id == node_id]
        return sum(1 for r in records if not r.success)

    def summary(self) -> dict[str, Any]:
        """Summary dict with total, success_rate, avg_latency, error_count."""
        return {
            "total": self.total_invocations(),
            "success_rate": self.success_rate(),
            "avg_latency": self.avg_latency_ms(),
            "error_count": self.error_count(),
        }
