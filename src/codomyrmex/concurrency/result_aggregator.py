"""Result aggregation from distributed workers.

Collects TaskResults from multiple workers, merges into
an AggregateResult with statistics.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .tasks.task_worker import TaskResult


@dataclass
class AggregateResult:
    """Aggregated results from multiple workers.

    Attributes:
        total_tasks: Total tasks processed.
        successful: Number of successful tasks.
        failed: Number of failed tasks.
        results: Individual task results.
        mean_duration_ms: Average processing time.
        worker_stats: Per-worker statistics.
    """

    total_tasks: int = 0
    successful: int = 0
    failed: int = 0
    results: list[TaskResult] = field(default_factory=list)
    mean_duration_ms: float = 0.0
    worker_stats: dict[str, dict[str, int]] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        return self.successful / self.total_tasks if self.total_tasks > 0 else 0.0


class ResultAggregator:
    """Collect and aggregate results from distributed workers.

    Example::

        aggregator = ResultAggregator()
        aggregator.add(result1)
        aggregator.add(result2)
        summary = aggregator.aggregate()
    """

    def __init__(self) -> None:
        self._results: list[TaskResult] = []

    @property
    def count(self) -> int:
        """count ."""
        return len(self._results)

    def add(self, result: TaskResult) -> None:
        """Add a task result."""
        self._results.append(result)

    def add_batch(self, results: list[TaskResult]) -> None:
        """Add multiple results at once."""
        self._results.extend(results)

    def aggregate(self) -> AggregateResult:
        """Compute aggregated statistics.

        Returns:
            AggregateResult with summary metrics.
        """
        total = len(self._results)
        successful = sum(1 for r in self._results if r.success)
        failed = total - successful
        durations = [r.duration_ms for r in self._results]
        mean_dur = sum(durations) / len(durations) if durations else 0.0

        # Per-worker stats
        worker_stats: dict[str, dict[str, int]] = {}
        for r in self._results:
            if r.worker_id not in worker_stats:
                worker_stats[r.worker_id] = {"success": 0, "failed": 0}
            if r.success:
                worker_stats[r.worker_id]["success"] += 1
            else:
                worker_stats[r.worker_id]["failed"] += 1

        return AggregateResult(
            total_tasks=total,
            successful=successful,
            failed=failed,
            results=list(self._results),
            mean_duration_ms=mean_dur,
            worker_stats=worker_stats,
        )

    def clear(self) -> None:
        """Clear all collected results."""
        self._results.clear()


__all__ = ["AggregateResult", "ResultAggregator"]
