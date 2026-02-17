"""Unit tests for prompt_testing module."""
import pytest


@pytest.mark.unit
class TestPromptTestingImports:
    """Test suite for prompt_testing module imports."""

    def test_module_imports(self):
        """Verify module can be imported without errors."""
        from codomyrmex.prompt_engineering import testing as prompt_testing
        assert prompt_testing is not None

    def test_public_api_exists(self):
        """Verify expected public API is available."""
        from codomyrmex.prompt_engineering.testing import __all__
        expected_exports = [
            "EvaluationType",
            "TestStatus",
            "PromptTestCase",
            "TestResult",
            "TestSuiteResult",
            "Evaluator",
            "ExactMatchEvaluator",
            "ContainsEvaluator",
            "CustomEvaluator",
            "PromptTestSuite",
            "PromptTester",
            "ABTest",
        ]
        for export in expected_exports:
            assert export in __all__, f"Missing export: {export}"


@pytest.mark.unit
class TestEvaluationType:
    """Test suite for EvaluationType enum."""

    def test_evaluation_type_values(self):
        """Verify all evaluation types are available."""
        from codomyrmex.prompt_engineering.testing import EvaluationType

        assert EvaluationType.EXACT_MATCH.value == "exact_match"
        assert EvaluationType.CONTAINS.value == "contains"
        assert EvaluationType.NOT_CONTAINS.value == "not_contains"
        assert EvaluationType.SEMANTIC.value == "semantic"
        assert EvaluationType.CUSTOM.value == "custom"


@pytest.mark.unit
class TestTestStatus:
    """Test suite for TestStatus enum."""

    def test_status_values(self):
        """Verify all test statuses are available."""
        from codomyrmex.prompt_engineering.testing import TestStatus

        assert TestStatus.PENDING.value == "pending"
        assert TestStatus.RUNNING.value == "running"
        assert TestStatus.PASSED.value == "passed"
        assert TestStatus.FAILED.value == "failed"
        assert TestStatus.ERROR.value == "error"


@pytest.mark.unit
class TestPromptTestCase:
    """Test suite for PromptTestCase dataclass."""

    def test_test_case_creation(self):
        """Verify PromptTestCase can be created."""
        from codomyrmex.prompt_engineering.testing import EvaluationType, PromptTestCase

        test_case = PromptTestCase(
            id="greeting_test",
            prompt="Say hello to the user",
            expected_contains=["hello", "hi"],
            evaluation_type=EvaluationType.CONTAINS,
        )

        assert test_case.id == "greeting_test"
        assert "hello" in test_case.expected_contains

    def test_test_case_to_dict(self):
        """Verify test case serialization."""
        from codomyrmex.prompt_engineering.testing import PromptTestCase

        test_case = PromptTestCase(
            id="test",
            prompt="Test prompt",
            weight=2.0,
        )

        result = test_case.to_dict()
        assert result["id"] == "test"
        assert result["weight"] == 2.0


@pytest.mark.unit
class TestTestResult:
    """Test suite for TestResult dataclass."""

    def test_result_creation(self):
        """Verify TestResult can be created."""
        from codomyrmex.prompt_engineering.testing import TestResult, TestStatus

        result = TestResult(
            test_case_id="test_1",
            status=TestStatus.PASSED,
            actual_output="Hello, user!",
            score=1.0,
            latency_ms=150.0,
        )

        assert result.test_case_id == "test_1"
        assert result.passed is True

    def test_result_passed_property(self):
        """Verify passed property."""
        from codomyrmex.prompt_engineering.testing import TestResult, TestStatus

        passed = TestResult(
            test_case_id="1",
            status=TestStatus.PASSED,
        )
        assert passed.passed is True

        failed = TestResult(
            test_case_id="2",
            status=TestStatus.FAILED,
        )
        assert failed.passed is False

    def test_result_to_dict(self):
        """Verify result serialization."""
        from codomyrmex.prompt_engineering.testing import TestResult, TestStatus

        result = TestResult(
            test_case_id="test",
            status=TestStatus.PASSED,
            score=0.9,
        )

        data = result.to_dict()
        assert data["status"] == "passed"
        assert data["score"] == 0.9


@pytest.mark.unit
class TestTestSuiteResult:
    """Test suite for TestSuiteResult dataclass."""

    def test_suite_result_creation(self):
        """Verify TestSuiteResult can be created."""
        from codomyrmex.prompt_engineering.testing import TestSuiteResult

        result = TestSuiteResult(
            suite_id="my_suite",
            prompt_version="v1.0",
        )

        assert result.suite_id == "my_suite"
        assert result.total_tests == 0

    def test_suite_result_metrics(self):
        """Verify suite result metrics."""
        from codomyrmex.prompt_engineering.testing import TestResult, TestStatus, TestSuiteResult

        result = TestSuiteResult(suite_id="test", prompt_version="v1")
        result.results = [
            TestResult(test_case_id="1", status=TestStatus.PASSED, score=1.0, latency_ms=100),
            TestResult(test_case_id="2", status=TestStatus.PASSED, score=0.8, latency_ms=200),
            TestResult(test_case_id="3", status=TestStatus.FAILED, score=0.3, latency_ms=150),
        ]

        assert result.total_tests == 3
        assert result.passed_tests == 2
        assert result.failed_tests == 1
        assert result.pass_rate == 2/3
        assert result.average_latency_ms == 150.0
        assert abs(result.average_score - 0.7) < 0.01

    def test_suite_result_to_dict(self):
        """Verify suite result serialization."""
        from codomyrmex.prompt_engineering.testing import TestSuiteResult

        result = TestSuiteResult(suite_id="test", prompt_version="v1.0")
        data = result.to_dict()

        assert data["suite_id"] == "test"
        assert data["prompt_version"] == "v1.0"


@pytest.mark.unit
class TestExactMatchEvaluator:
    """Test suite for ExactMatchEvaluator."""

    def test_exact_match_pass(self):
        """Verify exact match passes."""
        from codomyrmex.prompt_engineering.testing import ExactMatchEvaluator, PromptTestCase

        evaluator = ExactMatchEvaluator()
        test_case = PromptTestCase(
            id="test",
            prompt="test",
            expected_output="Hello World",
        )

        score = evaluator.evaluate(test_case, "Hello World")
        assert score == 1.0

    def test_exact_match_fail(self):
        """Verify exact match fails on mismatch."""
        from codomyrmex.prompt_engineering.testing import ExactMatchEvaluator, PromptTestCase

        evaluator = ExactMatchEvaluator()
        test_case = PromptTestCase(
            id="test",
            prompt="test",
            expected_output="Hello World",
        )

        score = evaluator.evaluate(test_case, "Goodbye World")
        assert score == 0.0

    def test_exact_match_case_insensitive(self):
        """Verify case-insensitive matching."""
        from codomyrmex.prompt_engineering.testing import ExactMatchEvaluator, PromptTestCase

        evaluator = ExactMatchEvaluator(case_sensitive=False)
        test_case = PromptTestCase(
            id="test",
            prompt="test",
            expected_output="Hello World",
        )

        score = evaluator.evaluate(test_case, "hello world")
        assert score == 1.0


@pytest.mark.unit
class TestContainsEvaluator:
    """Test suite for ContainsEvaluator."""

    def test_contains_all_present(self):
        """Verify contains evaluator with all terms present."""
        from codomyrmex.prompt_engineering.testing import ContainsEvaluator, PromptTestCase

        evaluator = ContainsEvaluator()
        test_case = PromptTestCase(
            id="test",
            prompt="test",
            expected_contains=["hello", "world"],
        )

        score = evaluator.evaluate(test_case, "hello world, how are you?")
        assert score == 1.0

    def test_contains_partial_match(self):
        """Verify partial match scoring."""
        from codomyrmex.prompt_engineering.testing import ContainsEvaluator, PromptTestCase

        evaluator = ContainsEvaluator()
        test_case = PromptTestCase(
            id="test",
            prompt="test",
            expected_contains=["hello", "world", "missing"],
        )

        score = evaluator.evaluate(test_case, "hello world")
        assert score == 2/3

    def test_not_contains(self):
        """Verify not_contains evaluation."""
        from codomyrmex.prompt_engineering.testing import ContainsEvaluator, PromptTestCase

        evaluator = ContainsEvaluator()
        test_case = PromptTestCase(
            id="test",
            prompt="test",
            expected_not_contains=["error", "fail"],
        )

        score = evaluator.evaluate(test_case, "success!")
        assert score == 1.0

    def test_mixed_contains_and_not_contains(self):
        """Verify mixed contains/not_contains."""
        from codomyrmex.prompt_engineering.testing import ContainsEvaluator, PromptTestCase

        evaluator = ContainsEvaluator()
        test_case = PromptTestCase(
            id="test",
            prompt="test",
            expected_contains=["success"],
            expected_not_contains=["error"],
        )

        # Both conditions met
        score = evaluator.evaluate(test_case, "operation success")
        assert score == 1.0


@pytest.mark.unit
class TestCustomEvaluator:
    """Test suite for CustomEvaluator."""

    def test_custom_function(self):
        """Verify custom evaluation function."""
        from codomyrmex.prompt_engineering.testing import CustomEvaluator, PromptTestCase

        def length_evaluator(tc, output):
            return min(len(output) / 100, 1.0)

        evaluator = CustomEvaluator(eval_fn=length_evaluator)
        test_case = PromptTestCase(id="test", prompt="test")

        score = evaluator.evaluate(test_case, "x" * 50)
        assert score == 0.5


@pytest.mark.unit
class TestPromptTestSuite:
    """Test suite for PromptTestSuite."""

    def test_suite_creation(self):
        """Verify suite creation."""
        from codomyrmex.prompt_engineering.testing import PromptTestSuite

        suite = PromptTestSuite(
            suite_id="greeting_tests",
            description="Tests for greeting prompts",
        )

        assert suite.suite_id == "greeting_tests"
        assert len(suite) == 0

    def test_suite_add_test(self):
        """Verify test addition."""
        from codomyrmex.prompt_engineering.testing import PromptTestCase, PromptTestSuite

        suite = PromptTestSuite(suite_id="test")
        suite.add_test(PromptTestCase(id="t1", prompt="Test 1"))
        suite.add_test(PromptTestCase(id="t2", prompt="Test 2"))

        assert len(suite) == 2

    def test_suite_add_tests_batch(self):
        """Verify batch test addition."""
        from codomyrmex.prompt_engineering.testing import PromptTestCase, PromptTestSuite

        suite = PromptTestSuite(suite_id="test")
        suite.add_tests([
            PromptTestCase(id="t1", prompt="Test 1"),
            PromptTestCase(id="t2", prompt="Test 2"),
            PromptTestCase(id="t3", prompt="Test 3"),
        ])

        assert len(suite) == 3

    def test_suite_get_test(self):
        """Verify test retrieval."""
        from codomyrmex.prompt_engineering.testing import PromptTestCase, PromptTestSuite

        suite = PromptTestSuite(suite_id="test")
        suite.add_test(PromptTestCase(id="target", prompt="Find me"))

        found = suite.get_test("target")
        assert found is not None
        assert found.prompt == "Find me"

        missing = suite.get_test("nonexistent")
        assert missing is None

    def test_suite_chaining(self):
        """Verify method chaining."""
        from codomyrmex.prompt_engineering.testing import PromptTestCase, PromptTestSuite

        suite = (
            PromptTestSuite(suite_id="test")
            .add_test(PromptTestCase(id="t1", prompt="Test 1"))
            .add_test(PromptTestCase(id="t2", prompt="Test 2"))
        )

        assert len(suite) == 2


@pytest.mark.unit
class TestPromptTester:
    """Test suite for PromptTester."""

    def test_tester_creation(self):
        """Verify tester creation."""
        from codomyrmex.prompt_engineering.testing import PromptTester

        tester = PromptTester(pass_threshold=0.7)
        assert tester.pass_threshold == 0.7

    def test_tester_run_suite(self):
        """Verify suite execution."""
        from codomyrmex.prompt_engineering.testing import (
            PromptTestCase,
            PromptTester,
            PromptTestSuite,
        )

        def mock_executor(prompt):
            return f"Response to: {prompt}"

        suite = PromptTestSuite(suite_id="test")
        suite.add_test(PromptTestCase(
            id="t1",
            prompt="Say hello",
            expected_contains=["Response"],
        ))

        tester = PromptTester()
        results = tester.run(suite, mock_executor, prompt_version="v1")

        assert results.total_tests == 1
        assert results.passed_tests == 1

    def test_tester_handles_executor_error(self):
        """Verify error handling in executor."""
        from codomyrmex.prompt_engineering.testing import (
            PromptTestCase,
            PromptTester,
            PromptTestSuite,
            TestStatus,
        )

        def failing_executor(prompt):
            raise ValueError("Executor error")

        suite = PromptTestSuite(suite_id="test")
        suite.add_test(PromptTestCase(id="t1", prompt="Test"))

        tester = PromptTester()
        results = tester.run(suite, failing_executor)

        assert results.results[0].status == TestStatus.ERROR

    def test_tester_register_evaluator(self):
        """Verify custom evaluator registration."""
        from codomyrmex.prompt_engineering.testing import (
            CustomEvaluator,
            EvaluationType,
            PromptTestCase,
            PromptTester,
            PromptTestSuite,
        )

        custom_eval = CustomEvaluator(lambda tc, out: 1.0 if "magic" in out else 0.0)

        suite = PromptTestSuite(suite_id="test")
        suite.add_test(PromptTestCase(
            id="t1",
            prompt="Test",
            evaluation_type=EvaluationType.CUSTOM,
        ))

        tester = PromptTester()
        tester.register_evaluator(EvaluationType.CUSTOM, custom_eval)

        results = tester.run(suite, lambda p: "magic word")
        assert results.results[0].score == 1.0


@pytest.mark.unit
class TestABTest:
    """Test suite for ABTest."""

    def test_ab_test_creation(self):
        """Verify A/B test creation."""
        from codomyrmex.prompt_engineering.testing import ABTest

        ab_test = ABTest(test_id="headline_experiment")
        assert ab_test.test_id == "headline_experiment"

    def test_ab_test_add_variant(self):
        """Verify variant addition."""
        from codomyrmex.prompt_engineering.testing import ABTest

        ab_test = ABTest(test_id="test")
        ab_test.add_variant("control", "Original prompt: {input}")
        ab_test.add_variant("treatment", "New prompt: {input}")

        assert len(ab_test.variants) == 2

    def test_ab_test_chaining(self):
        """Verify method chaining."""
        from codomyrmex.prompt_engineering.testing import ABTest

        ab_test = (
            ABTest(test_id="test")
            .add_variant("a", "Prompt A")
            .add_variant("b", "Prompt B")
        )

        assert "a" in ab_test.variants
        assert "b" in ab_test.variants

    def test_ab_test_run(self):
        """Verify A/B test execution."""
        from codomyrmex.prompt_engineering.testing import ABTest, PromptTestCase, PromptTestSuite

        suite = PromptTestSuite(suite_id="test")
        suite.add_test(PromptTestCase(
            id="t1",
            prompt="Hello",
            expected_contains=["response"],
        ))

        ab_test = ABTest(test_id="experiment")
        ab_test.add_variant("control", "Control prompt")
        ab_test.add_variant("treatment", "Treatment prompt")

        def executor_factory(template):
            return lambda prompt: f"response from {template}"

        results = ab_test.run(suite, executor_factory)

        assert "control" in results
        assert "treatment" in results

    def test_ab_test_get_winner(self):
        """Verify winner determination."""
        from codomyrmex.prompt_engineering.testing import (
            ABTest,
            TestResult,
            TestStatus,
            TestSuiteResult,
        )

        ab_test = ABTest(test_id="test")

        # Manually set results
        control_result = TestSuiteResult(suite_id="test", prompt_version="control")
        control_result.results = [
            TestResult(test_case_id="1", status=TestStatus.PASSED, score=0.8, latency_ms=100),
        ]

        treatment_result = TestSuiteResult(suite_id="test", prompt_version="treatment")
        treatment_result.results = [
            TestResult(test_case_id="1", status=TestStatus.PASSED, score=0.9, latency_ms=100),
        ]

        ab_test.results = {
            "control": control_result,
            "treatment": treatment_result,
        }

        winner = ab_test.get_winner(metric="average_score")
        assert winner == "treatment"

    def test_ab_test_compare(self):
        """Verify comparison report generation."""
        from codomyrmex.prompt_engineering.testing import (
            ABTest,
            TestResult,
            TestStatus,
            TestSuiteResult,
        )

        ab_test = ABTest(test_id="test")

        result_a = TestSuiteResult(suite_id="test", prompt_version="a")
        result_a.results = [
            TestResult(test_case_id="1", status=TestStatus.PASSED, score=0.9, latency_ms=100),
        ]

        result_b = TestSuiteResult(suite_id="test", prompt_version="b")
        result_b.results = [
            TestResult(test_case_id="1", status=TestStatus.FAILED, score=0.4, latency_ms=200),
        ]

        ab_test.results = {"a": result_a, "b": result_b}

        comparison = ab_test.compare()

        assert "a" in comparison
        assert "b" in comparison
        assert comparison["a"]["pass_rate"] == 1.0
        assert comparison["b"]["pass_rate"] == 0.0
