"""Zero-mock tests for prompt_engineering.testing.models."""

from __future__ import annotations

import pytest

from codomyrmex.prompt_engineering.testing.models import (
    EvaluationType,
    PromptTestCase,
    TestResult,
    TestStatus,
    TestSuiteResult,
)


def _make_result(status=TestStatus.PASSED, score=1.0, latency=50.0, error=None):
    return TestResult(
        test_case_id="tc-1",
        status=status,
        actual_output="response",
        score=score,
        latency_ms=latency,
        error=error,
    )


@pytest.mark.unit
class TestEvaluationType:
    def test_all_values_unique(self):
        values = [e.value for e in EvaluationType]
        assert len(values) == len(set(values))

    def test_contains_member(self):
        assert EvaluationType("contains") == EvaluationType.CONTAINS

    def test_exact_match_value(self):
        assert EvaluationType.EXACT_MATCH.value == "exact_match"


@pytest.mark.unit
class TestTestStatus:
    def test_passed_value(self):
        assert TestStatus.PASSED.value == "passed"

    def test_failed_value(self):
        assert TestStatus.FAILED.value == "failed"

    def test_all_members_present(self):
        names = {s.name for s in TestStatus}
        assert {"PENDING", "RUNNING", "PASSED", "FAILED", "ERROR"} <= names


@pytest.mark.unit
class TestPromptTestCase:
    def test_minimal_construction(self):
        tc = PromptTestCase(id="t1", prompt="Say hello")
        assert tc.id == "t1"
        assert tc.prompt == "Say hello"
        assert tc.weight == 1.0
        assert tc.evaluation_type == EvaluationType.CONTAINS

    def test_to_dict_keys(self):
        tc = PromptTestCase(id="t2", prompt="x")
        d = tc.to_dict()
        assert "id" in d
        assert "prompt" in d
        assert "evaluation_type" in d
        assert d["evaluation_type"] == EvaluationType.CONTAINS.value

    def test_expected_contains_list(self):
        tc = PromptTestCase(id="t3", prompt="y", expected_contains=["hello", "world"])
        assert len(tc.expected_contains) == 2

    def test_custom_weight(self):
        tc = PromptTestCase(id="t4", prompt="z", weight=2.5)
        assert tc.weight == 2.5


@pytest.mark.unit
class TestTestResult:
    def test_passed_property_true(self):
        r = _make_result(status=TestStatus.PASSED)
        assert r.passed is True

    def test_passed_property_false_for_failed(self):
        r = _make_result(status=TestStatus.FAILED)
        assert r.passed is False

    def test_passed_property_false_for_error(self):
        r = _make_result(status=TestStatus.ERROR, error="timeout")
        assert r.passed is False

    def test_to_dict_contains_status_string(self):
        r = _make_result()
        d = r.to_dict()
        assert d["status"] == TestStatus.PASSED.value

    def test_to_dict_preserves_score(self):
        r = _make_result(score=0.75)
        assert r.to_dict()["score"] == 0.75

    def test_error_propagated(self):
        r = _make_result(status=TestStatus.ERROR, error="connection refused")
        assert r.error == "connection refused"


@pytest.mark.unit
class TestTestSuiteResult:
    def _suite_with_results(self, results):
        return TestSuiteResult(
            suite_id="s1", prompt_version="v1.0", results=results
        )

    def test_empty_suite(self):
        suite = self._suite_with_results([])
        assert suite.total_tests == 0
        assert suite.pass_rate == 0.0
        assert suite.average_latency_ms == 0.0
        assert suite.average_score == 0.0

    def test_all_passed(self):
        results = [_make_result(TestStatus.PASSED) for _ in range(5)]
        suite = self._suite_with_results(results)
        assert suite.total_tests == 5
        assert suite.passed_tests == 5
        assert suite.pass_rate == 1.0

    def test_mixed_pass_fail(self):
        results = [
            _make_result(TestStatus.PASSED),
            _make_result(TestStatus.PASSED),
            _make_result(TestStatus.FAILED),
        ]
        suite = self._suite_with_results(results)
        assert suite.passed_tests == 2
        assert suite.failed_tests == 1
        assert suite.pass_rate == pytest.approx(2 / 3)

    def test_average_latency(self):
        results = [_make_result(latency=100.0), _make_result(latency=200.0)]
        suite = self._suite_with_results(results)
        assert suite.average_latency_ms == pytest.approx(150.0)

    def test_average_score(self):
        results = [_make_result(score=0.6), _make_result(score=0.8)]
        suite = self._suite_with_results(results)
        assert suite.average_score == pytest.approx(0.7)

    def test_worst_tests_ordering(self):
        results = [
            _make_result(score=0.9),
            _make_result(score=0.1),
            _make_result(score=0.5),
        ]
        suite = self._suite_with_results(results)
        worst = suite.worst_tests(n=1)
        assert len(worst) == 1
        assert worst[0].score == pytest.approx(0.1)

    def test_to_dict_pass_rate(self):
        results = [_make_result(TestStatus.PASSED), _make_result(TestStatus.FAILED)]
        suite = self._suite_with_results(results)
        d = suite.to_dict()
        assert d["pass_rate"] == pytest.approx(0.5)
        assert d["total_tests"] == 2

    def test_completed_at_none_by_default(self):
        suite = self._suite_with_results([])
        assert suite.completed_at is None
        d = suite.to_dict()
        assert d["completed_at"] is None

    def test_independent_results_per_instance(self):
        s1 = self._suite_with_results([])
        s2 = self._suite_with_results([])
        s1.results.append(_make_result())
        assert len(s2.results) == 0
