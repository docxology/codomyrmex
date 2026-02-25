"""
Benchmark suite management for model evaluation.

Provides dataclasses and classes for defining benchmark cases,
running them against scorers, and collecting structured results.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .scorers import ExactMatchScorer, Scorer


@dataclass
class BenchmarkCase:
    """A single benchmark test case.

    Attributes:
        id: Unique identifier for the case. Auto-generated if not provided.
        input_text: The input prompt or text to send to the model.
        expected_output: The expected/reference output for scoring.
        metadata: Arbitrary metadata for categorization and filtering.
        tags: Tags for grouping and filtering benchmark cases.
    """
    input_text: str
    expected_output: str
    id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Execute   Post Init   operations natively."""
        if not self.id:
            self.id = str(uuid.uuid4())[:8]


@dataclass
class BenchmarkResult:
    """Result from running a single benchmark case.

    Attributes:
        case_id: The ID of the benchmark case that was run.
        score: The numerical score from the scorer (0.0 to 1.0).
        duration_ms: Time taken to produce the output, in milliseconds.
        scorer_name: Name of the scorer used to evaluate this case.
        actual_output: The actual output produced by the model.
        metadata: Additional metadata about the run.
    """
    case_id: str
    score: float
    duration_ms: float
    scorer_name: str
    actual_output: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        """Whether this result meets a passing threshold (>= 0.5)."""
        return self.score >= 0.5

    def to_dict(self) -> dict[str, Any]:
        """Convert to a plain dictionary."""
        return {
            "case_id": self.case_id,
            "score": self.score,
            "duration_ms": self.duration_ms,
            "scorer_name": self.scorer_name,
            "actual_output": self.actual_output,
            "passed": self.passed,
            "metadata": self.metadata,
        }


@dataclass
class SuiteResult:
    """Aggregated results from running an entire benchmark suite.

    Attributes:
        suite_name: Name of the benchmark suite.
        results: Individual results for each benchmark case.
        total_duration_ms: Total time for all cases in milliseconds.
        metadata: Additional metadata about the suite run.
    """
    suite_name: str
    results: list[BenchmarkResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_cases(self) -> int:
        """Total number of cases evaluated."""
        return len(self.results)

    @property
    def passed_cases(self) -> int:
        """Number of cases that passed (score >= 0.5)."""
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_cases(self) -> int:
        """Number of cases that failed (score < 0.5)."""
        return self.total_cases - self.passed_cases

    @property
    def average_score(self) -> float:
        """Average score across all cases."""
        if not self.results:
            return 0.0
        return round(
            sum(r.score for r in self.results) / len(self.results), 6
        )

    @property
    def pass_rate(self) -> float:
        """Fraction of cases that passed."""
        if not self.results:
            return 0.0
        return round(self.passed_cases / self.total_cases, 6)

    def get_result(self, case_id: str) -> BenchmarkResult | None:
        """Get the result for a specific case ID."""
        for r in self.results:
            if r.case_id == case_id:
                return r
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to a plain dictionary."""
        return {
            "suite_name": self.suite_name,
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "average_score": self.average_score,
            "pass_rate": self.pass_rate,
            "total_duration_ms": self.total_duration_ms,
            "results": [r.to_dict() for r in self.results],
            "metadata": self.metadata,
        }

    def to_result(self) -> Result | None:
        """Convert to a codomyrmex Result if schemas are available."""
        if Result is None or ResultStatus is None:
            return None

        status = (
            ResultStatus.SUCCESS
            if self.pass_rate >= 0.5
            else ResultStatus.FAILURE
        )
        return Result(
            status=status,
            data=self.to_dict(),
            message=f"Suite '{self.suite_name}': {self.passed_cases}/{self.total_cases} passed "
                    f"(avg score: {self.average_score})",
            duration_ms=self.total_duration_ms,
            metadata={"suite_name": self.suite_name},
        )


class BenchmarkSuite:
    """A collection of benchmark cases that can be run against a model function.

    The suite manages benchmark cases, runs them through a provided
    model function, scores the outputs, and collects structured results.

    Args:
        name: Human-readable name for this benchmark suite.
        scorer: The scorer to use for evaluation. Defaults to ExactMatchScorer.
    """

    def __init__(
        self,
        name: str = "default",
        scorer: Scorer | None = None,
    ) -> None:
        """Execute   Init   operations natively."""
        self._name = name
        self._scorer = scorer or ExactMatchScorer(case_sensitive=False)
        self._cases: list[BenchmarkCase] = []

    @property
    def name(self) -> str:
        """Name of this benchmark suite."""
        return self._name

    @property
    def cases(self) -> list[BenchmarkCase]:
        """All benchmark cases in this suite (read-only copy)."""
        return list(self._cases)

    @property
    def case_count(self) -> int:
        """Number of cases in this suite."""
        return len(self._cases)

    def add_case(
        self,
        input_text: str,
        expected_output: str,
        case_id: str = "",
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> BenchmarkCase:
        """Add a benchmark case to the suite.

        Args:
            input_text: The input text for the case.
            expected_output: The expected output for scoring.
            case_id: Optional case ID. Auto-generated if empty.
            metadata: Optional metadata dict.
            tags: Optional tags for filtering.

        Returns:
            The created BenchmarkCase.
        """
        case = BenchmarkCase(
            id=case_id,
            input_text=input_text,
            expected_output=expected_output,
            metadata=metadata or {},
            tags=tags or [],
        )
        self._cases.append(case)
        return case

    def add_cases(self, cases: list[BenchmarkCase]) -> None:
        """Add multiple pre-built benchmark cases.

        Args:
            cases: List of BenchmarkCase instances to add.
        """
        self._cases.extend(cases)

    def remove_case(self, case_id: str) -> bool:
        """Remove a case by its ID.

        Args:
            case_id: The ID of the case to remove.

        Returns:
            True if the case was found and removed, False otherwise.
        """
        original_count = len(self._cases)
        self._cases = [c for c in self._cases if c.id != case_id]
        return len(self._cases) < original_count

    def get_cases_by_tag(self, tag: str) -> list[BenchmarkCase]:
        """Filter cases by a specific tag.

        Args:
            tag: The tag to filter by.

        Returns:
            List of cases that have the specified tag.
        """
        return [c for c in self._cases if tag in c.tags]

    def run(
        self,
        model_fn: Callable[[str], str],
        scorer: Scorer | None = None,
    ) -> SuiteResult:
        """Run all benchmark cases through the model function and score outputs.

        Args:
            model_fn: A callable that takes an input string and returns
                an output string. This represents the model being evaluated.
            scorer: Optional scorer override. If None, uses the suite's
                default scorer.

        Returns:
            A SuiteResult with all individual results and aggregate metrics.
        """
        active_scorer = scorer or self._scorer
        results: list[BenchmarkResult] = []
        suite_start = time.perf_counter()

        for case in self._cases:
            case_start = time.perf_counter()

            try:
                actual_output = model_fn(case.input_text)
            except Exception as exc:
                actual_output = f"ERROR: {exc}"

            case_end = time.perf_counter()
            duration_ms = round((case_end - case_start) * 1000, 3)

            score_value = active_scorer.score(actual_output, case.expected_output)

            results.append(BenchmarkResult(
                case_id=case.id,
                score=score_value,
                duration_ms=duration_ms,
                scorer_name=active_scorer.name,
                actual_output=actual_output,
                metadata=case.metadata,
            ))

        suite_end = time.perf_counter()
        total_duration_ms = round((suite_end - suite_start) * 1000, 3)

        return SuiteResult(
            suite_name=self._name,
            results=results,
            total_duration_ms=total_duration_ms,
            metadata={"scorer": active_scorer.name, "case_count": len(self._cases)},
        )

    def get_results(
        self,
        model_fn: Callable[[str], str],
        scorer: Scorer | None = None,
    ) -> list[BenchmarkResult]:
        """Convenience method: run the suite and return just the result list.

        Args:
            model_fn: The model function to evaluate.
            scorer: Optional scorer override.

        Returns:
            List of BenchmarkResult instances.
        """
        suite_result = self.run(model_fn, scorer)
        return suite_result.results

    def clear(self) -> None:
        """Remove all cases from the suite."""
        self._cases.clear()


__all__ = [
    "BenchmarkCase",
    "BenchmarkResult",
    "BenchmarkSuite",
    "SuiteResult",
]
