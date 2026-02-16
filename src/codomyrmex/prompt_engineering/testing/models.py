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
