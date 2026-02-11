"""Tests for agent evaluation: scorers, TestCase, AgentBenchmark."""

import pytest

from codomyrmex.agents.evaluation import (
    AgentBenchmark,
    BenchmarkResult,
    CompositeScorer,
    ContainsScorer,
    EvalResult,
    ExactMatchScorer,
    LengthScorer,
    TestCase,
)


# ── Scorers ───────────────────────────────────────────────────────────────


class TestExactMatchScorer:
    def test_exact_match(self):
        s = ExactMatchScorer(case_sensitive=True)
        assert s.score("hello", "hello") == 1.0
        assert s.score("Hello", "hello") == 0.0

    def test_case_insensitive(self):
        s = ExactMatchScorer(case_sensitive=False)
        assert s.score("HELLO", "hello") == 1.0


class TestContainsScorer:
    def test_contains(self):
        s = ContainsScorer()
        assert s.score("the quick brown fox", "quick brown") == 1.0
        assert s.score("the quick brown fox", "lazy dog") == 0.0

    def test_case_insensitive(self):
        s = ContainsScorer(case_sensitive=False)
        assert s.score("Hello World", "hello world") == 1.0


class TestLengthScorer:
    def test_exact_length(self):
        s = LengthScorer(target_length=5)
        assert s.score("hello") == 1.0

    def test_too_short(self):
        s = LengthScorer(target_length=10, tolerance=0.3)
        score = s.score("hi")
        assert 0.0 <= score < 1.0

    def test_too_long(self):
        s = LengthScorer(target_length=3, tolerance=0.3)
        score = s.score("a" * 100)
        assert 0.0 <= score < 1.0


class TestCompositeScorer:
    def test_weighted_combination(self):
        exact = ExactMatchScorer(case_sensitive=False)
        length = LengthScorer(target_length=5)
        composite = CompositeScorer([(exact, 1.0), (length, 1.0)])
        # "hello" matches expected exactly and has target length 5
        score = composite.score("hello", "hello")
        assert score == 1.0


# ── TestCase ──────────────────────────────────────────────────────────────


class TestTestCase:
    def test_exact_match(self):
        tc = TestCase(id="t1", prompt="say hi", expected_output="hi")
        passed, reasons = tc.check_output("hi")
        assert passed
        assert len(reasons) == 0

    def test_contains_check(self):
        tc = TestCase(id="t2", prompt="greet", expected_contains=["hello"])
        passed, reasons = tc.check_output("hello world")
        assert passed

    def test_not_contains_fails(self):
        tc = TestCase(id="t3", prompt="q", expected_not_contains=["error"])
        passed, reasons = tc.check_output("got an error")
        assert not passed

    def test_max_latency(self):
        tc = TestCase(id="t4", prompt="fast", max_latency_ms=100)
        # check_output doesn't validate latency — just content
        passed, _ = tc.check_output("ok")
        assert passed


# ── AgentBenchmark ────────────────────────────────────────────────────────


class TestAgentBenchmark:
    def test_run_simple(self):
        bench = AgentBenchmark()
        bench.add_test_case(TestCase(
            id="upper",
            prompt="uppercase hello",
            expected_contains=["HELLO"],
        ))

        def executor(agent, prompt):
            return agent(prompt)

        results = bench.run(
            agents={"upcaser": lambda prompt: prompt.split()[-1].upper()},
            executor=executor,
        )

        assert "upcaser" in results
        r = results["upcaser"]
        assert isinstance(r, BenchmarkResult)
        assert r.total_tests == 1
        assert r.passed_tests == 1
