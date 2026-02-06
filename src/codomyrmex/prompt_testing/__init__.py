"""
Prompt Testing Module

Systematic prompt evaluation and A/B testing.
"""

__version__ = "0.1.0"

import json
import statistics
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar
from collections.abc import Callable


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


class Evaluator(ABC):
    """Base class for output evaluators."""

    @abstractmethod
    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """Evaluate output and return score (0-1)."""
        pass


class ExactMatchEvaluator(Evaluator):
    """Evaluator for exact matches."""

    def __init__(self, case_sensitive: bool = False):
        self.case_sensitive = case_sensitive

    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """Check for exact match."""
        expected = test_case.expected_output
        actual = actual_output

        if not self.case_sensitive:
            expected = expected.lower()
            actual = actual.lower()

        return 1.0 if expected.strip() == actual.strip() else 0.0


class ContainsEvaluator(Evaluator):
    """Evaluator for substring containment."""

    def __init__(self, case_sensitive: bool = False):
        self.case_sensitive = case_sensitive

    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """Check for contains/not contains."""
        actual = actual_output if self.case_sensitive else actual_output.lower()

        total_checks = len(test_case.expected_contains) + len(test_case.expected_not_contains)
        if total_checks == 0:
            return 1.0

        passed = 0

        for term in test_case.expected_contains:
            check = term if self.case_sensitive else term.lower()
            if check in actual:
                passed += 1

        for term in test_case.expected_not_contains:
            check = term if self.case_sensitive else term.lower()
            if check not in actual:
                passed += 1

        return passed / total_checks


class CustomEvaluator(Evaluator):
    """Evaluator using custom function."""

    def __init__(self, eval_fn: Callable[[PromptTestCase, str], float]):
        self.eval_fn = eval_fn

    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """Apply custom evaluation function."""
        return self.eval_fn(test_case, actual_output)


class PromptTestSuite:
    """
    Collection of test cases for prompt evaluation.

    Usage:
        suite = PromptTestSuite("greeting_tests")

        suite.add_test(PromptTestCase(
            id="hello",
            prompt="Say hello",
            expected_contains=["hello", "hi"],
        ))

        suite.add_test(PromptTestCase(
            id="farewell",
            prompt="Say goodbye",
            expected_contains=["goodbye", "bye"],
        ))
    """

    def __init__(self, suite_id: str, description: str = ""):
        self.suite_id = suite_id
        self.description = description
        self.test_cases: list[PromptTestCase] = []

    def add_test(self, test_case: PromptTestCase) -> "PromptTestSuite":
        """Add a test case."""
        self.test_cases.append(test_case)
        return self

    def add_tests(self, test_cases: list[PromptTestCase]) -> "PromptTestSuite":
        """Add multiple test cases."""
        self.test_cases.extend(test_cases)
        return self

    def get_test(self, test_id: str) -> PromptTestCase | None:
        """Get test case by ID."""
        for tc in self.test_cases:
            if tc.id == test_id:
                return tc
        return None

    def __len__(self) -> int:
        return len(self.test_cases)


class PromptTester:
    """
    Main prompt testing engine.

    Usage:
        tester = PromptTester()

        # Define executor (calls your LLM)
        def executor(prompt: str) -> str:
            return llm_client.complete(prompt)

        # Run tests
        results = tester.run(
            suite=test_suite,
            executor=executor,
            prompt_version="v1.0",
        )

        print(f"Pass rate: {results.pass_rate:.1%}")
    """

    def __init__(self, pass_threshold: float = 0.5):
        self.pass_threshold = pass_threshold
        self._evaluators: dict[EvaluationType, Evaluator] = {
            EvaluationType.EXACT_MATCH: ExactMatchEvaluator(),
            EvaluationType.CONTAINS: ContainsEvaluator(),
        }

    def register_evaluator(self, eval_type: EvaluationType, evaluator: Evaluator) -> None:
        """Register custom evaluator."""
        self._evaluators[eval_type] = evaluator

    def run(
        self,
        suite: PromptTestSuite,
        executor: Callable[[str], str],
        prompt_version: str = "unknown",
    ) -> TestSuiteResult:
        """
        Run a test suite.

        Args:
            suite: The test suite to run
            executor: Function that executes prompts and returns output
            prompt_version: Version identifier for this prompt

        Returns:
            TestSuiteResult with all test results
        """
        suite_result = TestSuiteResult(
            suite_id=suite.suite_id,
            prompt_version=prompt_version,
        )

        for test_case in suite.test_cases:
            result = self._run_test(test_case, executor)
            suite_result.results.append(result)

        suite_result.completed_at = datetime.now()
        return suite_result

    def _run_test(
        self,
        test_case: PromptTestCase,
        executor: Callable[[str], str],
    ) -> TestResult:
        """Run a single test case."""
        start_time = time.time()

        try:
            # Execute prompt
            actual_output = executor(test_case.prompt)
            latency_ms = (time.time() - start_time) * 1000

            # Evaluate
            evaluator = self._evaluators.get(
                test_case.evaluation_type,
                ContainsEvaluator(),
            )
            score = evaluator.evaluate(test_case, actual_output)

            # Determine pass/fail
            status = TestStatus.PASSED if score >= self.pass_threshold else TestStatus.FAILED

            return TestResult(
                test_case_id=test_case.id,
                status=status,
                actual_output=actual_output,
                score=score,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_case_id=test_case.id,
                status=TestStatus.ERROR,
                error=str(e),
                latency_ms=latency_ms,
            )


class ABTest:
    """
    A/B testing for prompt variants.

    Usage:
        ab_test = ABTest("headline_test")
        ab_test.add_variant("control", control_prompt)
        ab_test.add_variant("treatment", treatment_prompt)

        results = ab_test.run(suite, executor)
        winner = ab_test.get_winner()
    """

    def __init__(self, test_id: str):
        self.test_id = test_id
        self.variants: dict[str, str] = {}
        self.results: dict[str, TestSuiteResult] = {}

    def add_variant(self, name: str, prompt_template: str) -> "ABTest":
        """Add a prompt variant."""
        self.variants[name] = prompt_template
        return self

    def run(
        self,
        suite: PromptTestSuite,
        executor_factory: Callable[[str], Callable[[str], str]],
    ) -> dict[str, TestSuiteResult]:
        """
        Run A/B test across all variants.

        Args:
            suite: Test suite to run
            executor_factory: Creates executor for each variant's prompt

        Returns:
            Dict mapping variant names to results
        """
        tester = PromptTester()

        for name, prompt_template in self.variants.items():
            executor = executor_factory(prompt_template)
            results = tester.run(suite, executor, prompt_version=name)
            self.results[name] = results

        return self.results

    def get_winner(self, metric: str = "pass_rate") -> str | None:
        """
        Get winning variant.

        Args:
            metric: Which metric to use (pass_rate, average_score, average_latency_ms)

        Returns:
            Name of winning variant
        """
        if not self.results:
            return None

        best_name = None
        best_value = float('-inf') if metric != "average_latency_ms" else float('inf')

        for name, result in self.results.items():
            value = getattr(result, metric, 0)

            if metric == "average_latency_ms":
                if value < best_value:
                    best_value = value
                    best_name = name
            else:
                if value > best_value:
                    best_value = value
                    best_name = name

        return best_name

    def compare(self) -> dict[str, dict[str, Any]]:
        """Generate comparison report."""
        report = {}
        for name, result in self.results.items():
            report[name] = {
                "pass_rate": result.pass_rate,
                "average_score": result.average_score,
                "average_latency_ms": result.average_latency_ms,
                "passed_tests": result.passed_tests,
                "total_tests": result.total_tests,
            }
        return report


__all__ = [
    # Enums
    "EvaluationType",
    "TestStatus",
    # Data classes
    "PromptTestCase",
    "TestResult",
    "TestSuiteResult",
    # Evaluators
    "Evaluator",
    "ExactMatchEvaluator",
    "ContainsEvaluator",
    "CustomEvaluator",
    # Core
    "PromptTestSuite",
    "PromptTester",
    "ABTest",
]
