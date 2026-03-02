"""
Prompt Testing Models

Data classes and enums for prompt testing.
"""

import statistics
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EvaluationType(Enum):
    """Types of prompt evaluation."""
    EXACT_MATCH = "exact_match"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    SEMANTIC = "semantic"
    CUSTOM = "custom"


class TestStatus(Enum):
    """Status of a test run."""
    __test__ = False
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


@dataclass
class PromptTestCase:
    """A single test case for prompt evaluation."""
    id: str
    prompt: str
    expected_output: str = ""
    evaluation_type: EvaluationType = EvaluationType.CONTAINS
    expected_contains: list[str] = field(default_factory=list)
    expected_not_contains: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "expected_output": self.expected_output,
            "evaluation_type": self.evaluation_type.value,
            "expected_contains": self.expected_contains,
            "expected_not_contains": self.expected_not_contains,
            "metadata": self.metadata,
            "weight": self.weight,
        }


@dataclass
class TestResult:
    """Result of running a single test case."""
    __test__ = False
    test_case_id: str
    status: TestStatus
    actual_output: str = ""
    score: float = 0.0
    latency_ms: float = 0.0
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        """Check if test passed."""
        return self.status == TestStatus.PASSED

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_case_id": self.test_case_id,
            "status": self.status.value,
            "actual_output": self.actual_output,
            "score": self.score,
            "latency_ms": self.latency_ms,
            "error": self.error,
            "details": self.details,
        }


@dataclass
class TestSuiteResult:
    """Result of running a complete test suite."""
    __test__ = False
    suite_id: str
    prompt_version: str
    results: list[TestResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tests(self) -> int:
        """Get total number of tests."""
        return len(self.results)

    @property
    def passed_tests(self) -> int:
        """Get number of passed tests."""
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_tests(self) -> int:
        """Get number of failed tests."""
        return sum(1 for r in self.results if r.status == TestStatus.FAILED)

    @property
    def pass_rate(self) -> float:
        """Get pass rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return self.passed_tests / self.total_tests

    @property
    def average_latency_ms(self) -> float:
        """Get average latency."""
        if not self.results:
            return 0.0
        return statistics.mean(r.latency_ms for r in self.results)

    @property
    def average_score(self) -> float:
        """Get average score."""
        if not self.results:
            return 0.0
        return statistics.mean(r.score for r in self.results)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "suite_id": self.suite_id,
            "prompt_version": self.prompt_version,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "pass_rate": self.pass_rate,
            "average_latency_ms": self.average_latency_ms,
            "average_score": self.average_score,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def worst_tests(self, n: int = 5) -> list[TestResult]:
        """Get the N worst-performing tests by score."""
        return sorted(self.results, key=lambda r: r.score)[:n]

    @property
    def error_tests(self) -> list[TestResult]:
        """Tests that errored during execution."""
        return [r for r in self.results if r.status == TestStatus.ERROR]

    @property
    def median_score(self) -> float:
        """Get median score."""
        if not self.results:
            return 0.0
        return statistics.median(r.score for r in self.results)

    @property
    def median_latency_ms(self) -> float:
        if not self.results:
            return 0.0
        return statistics.median(r.latency_ms for r in self.results)

    def score_distribution(self, buckets: int = 5) -> dict[str, int]:
        """Distribute scores into buckets for a histogram view."""
        if not self.results:
            return {}
        step = 1.0 / buckets
        dist: dict[str, int] = {}
        for i in range(buckets):
            lo = round(i * step, 2)
            hi = round((i + 1) * step, 2)
            label = f"{lo:.2f}-{hi:.2f}"
            dist[label] = sum(1 for r in self.results if lo <= r.score < hi)
        # Capture perfect 1.0 scores in the last bucket
        last_label = list(dist.keys())[-1]
        dist[last_label] += sum(1 for r in self.results if r.score == 1.0)
        return dist

    def regression_check(self, baseline: "TestSuiteResult", threshold: float = 0.05) -> dict[str, Any]:
        """Compare against a baseline suite run to detect regressions.

        Args:
            baseline: Previous test suite result to compare against.
            threshold: Maximum acceptable drop in pass_rate or avg score.

        Returns:
            Dict with 'regressed' bool, 'pass_rate_delta', 'score_delta',
            and lists of improved/degraded test IDs.
        """
        pr_delta = self.pass_rate - baseline.pass_rate
        sc_delta = self.average_score - baseline.average_score

        baseline_scores = {r.test_case_id: r.score for r in baseline.results}
        improved: list[str] = []
        degraded: list[str] = []
        for r in self.results:
            bl_score = baseline_scores.get(r.test_case_id)
            if bl_score is not None:
                if r.score > bl_score + 0.01:
                    improved.append(r.test_case_id)
                elif r.score < bl_score - 0.01:
                    degraded.append(r.test_case_id)

        return {
            "regressed": pr_delta < -threshold or sc_delta < -threshold,
            "pass_rate_delta": round(pr_delta, 4),
            "score_delta": round(sc_delta, 4),
            "improved_tests": improved,
            "degraded_tests": degraded,
        }

    def markdown(self) -> str:
        """Generate a markdown report of the suite results."""
        lines = [
            f"## Test Suite: {self.suite_id} (v{self.prompt_version})",
            f"- Pass rate: **{self.pass_rate:.1%}** ({self.passed_tests}/{self.total_tests})",
            f"- Avg score: {self.average_score:.3f} | Median: {self.median_score:.3f}",
            f"- Avg latency: {self.average_latency_ms:.1f}ms | Median: {self.median_latency_ms:.1f}ms",
            "",
            "| Test | Status | Score | Latency |",
            "|------|--------|-------|---------|",
        ]
        for r in self.results:
            icon = "✅" if r.passed else ("⚠️" if r.status == TestStatus.ERROR else "❌")
            lines.append(f"| {r.test_case_id} | {icon} {r.status.value} | {r.score:.3f} | {r.latency_ms:.1f}ms |")
        return "\n".join(lines)

