"""
Prompt Testing Runner

Test suite, tester, and A/B testing for prompts.
"""

import time
from datetime import datetime
from typing import Any
from collections.abc import Callable

from .evaluators import ContainsEvaluator, Evaluator, ExactMatchEvaluator
from .models import (
    EvaluationType,
    PromptTestCase,
    TestResult,
    TestStatus,
    TestSuiteResult,
)


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
