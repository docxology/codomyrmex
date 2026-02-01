"""
Tests for Prompt Testing Module
"""

import pytest
from codomyrmex.prompt_testing import (
    EvaluationType,
    TestStatus,
    PromptTestCase,
    TestResult,
    TestSuiteResult,
    ExactMatchEvaluator,
    ContainsEvaluator,
    CustomEvaluator,
    PromptTestSuite,
    PromptTester,
    ABTest,
)


class TestPromptTestCase:
    """Tests for PromptTestCase."""
    
    def test_create(self):
        """Should create test case."""
        tc = PromptTestCase(id="test1", prompt="Say hello")
        assert tc.id == "test1"
        assert tc.evaluation_type == EvaluationType.CONTAINS
    
    def test_to_dict(self):
        """Should convert to dict."""
        tc = PromptTestCase(id="t", prompt="p", expected_contains=["a"])
        d = tc.to_dict()
        assert d["id"] == "t"
        assert "a" in d["expected_contains"]


class TestEvaluators:
    """Tests for evaluators."""
    
    def test_exact_match(self):
        """Should evaluate exact matches."""
        evaluator = ExactMatchEvaluator()
        tc = PromptTestCase(id="t", prompt="p", expected_output="hello")
        
        assert evaluator.evaluate(tc, "hello") == 1.0
        assert evaluator.evaluate(tc, "HELLO") == 1.0  # case insensitive
        assert evaluator.evaluate(tc, "world") == 0.0
    
    def test_exact_match_case_sensitive(self):
        """Should handle case sensitivity."""
        evaluator = ExactMatchEvaluator(case_sensitive=True)
        tc = PromptTestCase(id="t", prompt="p", expected_output="hello")
        
        assert evaluator.evaluate(tc, "hello") == 1.0
        assert evaluator.evaluate(tc, "HELLO") == 0.0
    
    def test_contains(self):
        """Should evaluate contains."""
        evaluator = ContainsEvaluator()
        tc = PromptTestCase(
            id="t",
            prompt="p",
            expected_contains=["hello", "world"],
        )
        
        assert evaluator.evaluate(tc, "hello world") == 1.0
        assert evaluator.evaluate(tc, "hello") == 0.5
        assert evaluator.evaluate(tc, "bye") == 0.0
    
    def test_not_contains(self):
        """Should evaluate not contains."""
        evaluator = ContainsEvaluator()
        tc = PromptTestCase(
            id="t",
            prompt="p",
            expected_not_contains=["error", "failed"],
        )
        
        assert evaluator.evaluate(tc, "success") == 1.0
        assert evaluator.evaluate(tc, "error occurred") == 0.5
    
    def test_custom_evaluator(self):
        """Should use custom function."""
        evaluator = CustomEvaluator(lambda tc, out: len(out) / 10)
        tc = PromptTestCase(id="t", prompt="p")
        
        assert evaluator.evaluate(tc, "12345") == 0.5


class TestPromptTestSuite:
    """Tests for PromptTestSuite."""
    
    def test_add_test(self):
        """Should add tests."""
        suite = PromptTestSuite("test_suite")
        suite.add_test(PromptTestCase(id="t1", prompt="p1"))
        suite.add_test(PromptTestCase(id="t2", prompt="p2"))
        
        assert len(suite) == 2
    
    def test_get_test(self):
        """Should get test by ID."""
        suite = PromptTestSuite("test_suite")
        suite.add_test(PromptTestCase(id="t1", prompt="p1"))
        
        assert suite.get_test("t1").id == "t1"
        assert suite.get_test("missing") is None


class TestPromptTester:
    """Tests for PromptTester."""
    
    def test_run_passing(self):
        """Should run tests and pass."""
        suite = PromptTestSuite("test")
        suite.add_test(PromptTestCase(
            id="hello",
            prompt="Say hello",
            expected_contains=["hello"],
        ))
        
        tester = PromptTester()
        results = tester.run(
            suite=suite,
            executor=lambda p: "hello world",
        )
        
        assert results.pass_rate == 1.0
        assert results.passed_tests == 1
    
    def test_run_failing(self):
        """Should run tests and fail."""
        suite = PromptTestSuite("test")
        suite.add_test(PromptTestCase(
            id="hello",
            prompt="Say hello",
            expected_contains=["hello"],
        ))
        
        tester = PromptTester()
        results = tester.run(
            suite=suite,
            executor=lambda p: "goodbye",
        )
        
        assert results.pass_rate == 0.0
        assert results.failed_tests == 1
    
    def test_executor_error(self):
        """Should handle executor errors."""
        suite = PromptTestSuite("test")
        suite.add_test(PromptTestCase(id="t", prompt="p"))
        
        def failing_executor(p):
            raise ValueError("API error")
        
        tester = PromptTester()
        results = tester.run(suite=suite, executor=failing_executor)
        
        assert results.results[0].status == TestStatus.ERROR


class TestTestSuiteResult:
    """Tests for TestSuiteResult."""
    
    def test_metrics(self):
        """Should calculate metrics."""
        result = TestSuiteResult(suite_id="s", prompt_version="v1")
        result.results.append(TestResult("t1", TestStatus.PASSED, score=1.0, latency_ms=100))
        result.results.append(TestResult("t2", TestStatus.FAILED, score=0.0, latency_ms=200))
        
        assert result.total_tests == 2
        assert result.passed_tests == 1
        assert result.pass_rate == 0.5
        assert result.average_latency_ms == 150


class TestABTest:
    """Tests for ABTest."""
    
    def test_add_variants(self):
        """Should add variants."""
        ab = ABTest("test")
        ab.add_variant("control", "v1")
        ab.add_variant("treatment", "v2")
        
        assert len(ab.variants) == 2
    
    def test_run_comparison(self):
        """Should run A/B comparison."""
        suite = PromptTestSuite("test")
        suite.add_test(PromptTestCase(id="t", prompt="p", expected_contains=["yes"]))
        
        ab = ABTest("test")
        ab.add_variant("good", "returns yes")
        ab.add_variant("bad", "returns no")
        
        def executor_factory(prompt):
            def executor(p):
                return "yes" if "yes" in prompt else "no"
            return executor
        
        ab.run(suite, executor_factory)
        
        winner = ab.get_winner()
        assert winner == "good"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
