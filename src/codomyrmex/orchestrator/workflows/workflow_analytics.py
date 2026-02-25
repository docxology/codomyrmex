"""Workflow analytics from journal entries.

Aggregates journal data to produce insights: failure hotspots,
duration trends, per-step success rates, and summary reports.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from codomyrmex.orchestrator.workflows.workflow_journal import (
    WorkflowJournal,
)


@dataclass
class WorkflowInsight:
    """Summary insight from workflow analytics.

    Attributes:
        total_workflows: Number of workflows analyzed.
        total_steps: Total step events.
        overall_success_rate: Fraction of successful workflows.
        mean_duration_ms: Average workflow duration.
        failure_hotspots: Top step names by failure count.
        step_success_rates: Per-step success rates.
    """

    total_workflows: int = 0
    total_steps: int = 0
    overall_success_rate: float = 0.0
    mean_duration_ms: float = 0.0
    failure_hotspots: list[tuple[str, int]] = field(default_factory=list)
    step_success_rates: dict[str, float] = field(default_factory=dict)


class WorkflowAnalytics:
    """Analyze workflow journal entries for patterns and insights.

    Example::

        analytics = WorkflowAnalytics(journal)
        hotspots = analytics.failure_hotspots(n=5)
        insight = analytics.generate_insight()
    """

    def __init__(self, journal: WorkflowJournal) -> None:
        """Execute   Init   operations natively."""
        self._journal = journal

    def failure_hotspots(self, n: int = 5) -> list[tuple[str, int]]:
        """Return the top-N step names by failure count.

        Args:
            n: Maximum number of hotspots.

        Returns:
            List of (step_name, failure_count) tuples, descending.
        """
        failures: dict[str, int] = defaultdict(int)
        for entry in self._journal.by_event_type("step"):
            if entry.status == "failed":
                failures[entry.step_name] += 1

        sorted_failures = sorted(failures.items(), key=lambda x: x[1], reverse=True)
        return sorted_failures[:n]

    def duration_trend(self, window: int = 10) -> list[float]:
        """Compute a moving average of workflow durations.

        Args:
            window: Moving average window size.

        Returns:
            List of averaged durations.
        """
        completions = self._journal.by_event_type("complete")
        durations = [e.duration_ms for e in completions]

        if not durations:
            return []

        averages = []
        for i in range(len(durations)):
            start = max(0, i - window + 1)
            chunk = durations[start : i + 1]
            averages.append(sum(chunk) / len(chunk))

        return averages

    def success_rate(self, step_name: str) -> float:
        """Compute the success rate for a specific step.

        Args:
            step_name: Step to analyze.

        Returns:
            Success rate in [0, 1]. Returns 0.0 if no data.
        """
        step_entries = [
            e for e in self._journal.by_event_type("step")
            if e.step_name == step_name
        ]

        if not step_entries:
            return 0.0

        completed = sum(1 for e in step_entries if e.status == "completed")
        return completed / len(step_entries)

    def generate_insight(self) -> WorkflowInsight:
        """Generate a summary insight from all journal data.

        Returns:
            WorkflowInsight with aggregated metrics.
        """
        completions = self._journal.by_event_type("complete")
        steps = self._journal.by_event_type("step")

        total_wf = len(completions)
        successful_wf = sum(1 for c in completions if c.status == "success")
        overall_rate = successful_wf / total_wf if total_wf > 0 else 0.0

        durations = [c.duration_ms for c in completions]
        mean_dur = sum(durations) / len(durations) if durations else 0.0

        # Per-step success rates
        step_totals: dict[str, int] = defaultdict(int)
        step_success: dict[str, int] = defaultdict(int)
        for s in steps:
            if s.step_name:
                step_totals[s.step_name] += 1
                if s.status == "completed":
                    step_success[s.step_name] += 1

        step_rates = {
            name: step_success[name] / total
            for name, total in step_totals.items()
            if total > 0
        }

        return WorkflowInsight(
            total_workflows=total_wf,
            total_steps=len(steps),
            overall_success_rate=overall_rate,
            mean_duration_ms=mean_dur,
            failure_hotspots=self.failure_hotspots(),
            step_success_rates=step_rates,
        )


__all__ = ["WorkflowAnalytics", "WorkflowInsight"]
