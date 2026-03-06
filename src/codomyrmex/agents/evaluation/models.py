"""Evaluation data models: MetricType, EvalResult, TestCase, BenchmarkResult."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MetricType(Enum):
    """Types of evaluation metrics."""

    LATENCY = "latency"
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    COHERENCE = "coherence"
    RELEVANCE = "relevance"
    COST = "cost"
    TOKEN_EFFICIENCY = "token_efficiency"
    CUSTOM = "custom"


@dataclass
class EvalResult:
    """Result of a single evaluation."""

    agent_id: str
    test_case_id: str
    passed: bool = True
    score: float = 0.0
    latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    output: str = ""
    expected: str = ""
    metrics: dict[str, float] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TestCase:
    """A test case for evaluation."""

    id: str
    prompt: str
    expected_output: str | None = None
    expected_contains: list[str] = field(default_factory=list)
    expected_not_contains: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    max_latency_ms: float | None = None

    def check_output(self, output: str) -> tuple[bool, list[str]]:
        """Check if output meets expectations. Returns (passed, failure_reasons)."""
        failures = []

        for expected in self.expected_contains:
            if expected.lower() not in output.lower():
                failures.append(f"Missing expected: '{expected}'")

        for forbidden in self.expected_not_contains:
            if forbidden.lower() in output.lower():
                failures.append(f"Contains forbidden: '{forbidden}'")

        return len(failures) == 0, failures


@dataclass
class BenchmarkResult:
    """Aggregated benchmark results for an agent."""

    agent_id: str
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    avg_score: float = 0.0
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    total_cost: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    errors: list[str] = field(default_factory=list)
    by_tag: dict[str, dict[str, Any]] = field(default_factory=dict)
    results: list[EvalResult] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate."""
        if self.total_tests > 0:
            return self.passed_tests / self.total_tests
        return 0.0

    @property
    def tokens_per_second(self) -> float:
        """Calculate tokens per second throughput."""
        total_tokens = self.total_input_tokens + self.total_output_tokens
        total_time_s = sum(r.latency_ms for r in self.results) / 1000
        if total_time_s > 0:
            return total_tokens / total_time_s
        return 0.0
