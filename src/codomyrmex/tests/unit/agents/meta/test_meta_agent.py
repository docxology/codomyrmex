"""Tests for Sprint 17: Meta-Agent Self-Improvement.

Tests for scoring, strategies, ab_testing, meta_agent.
"""

from __future__ import annotations

from codomyrmex.agents.meta.ab_testing import ABTestEngine, ABTestResult
from codomyrmex.agents.meta.meta_agent import MetaAgent
from codomyrmex.agents.meta.scoring import OutcomeScore, OutcomeScorer
from codomyrmex.agents.meta.strategies import Strategy, StrategyLibrary

# ── OutcomeScorer ────────────────────────────────────────────────


class TestOutcomeScorer:
    """Test suite for OutcomeScorer."""
    def test_perfect_score(self) -> None:
        """Test functionality: perfect score."""
        scorer = OutcomeScorer()
        s = scorer.score(tests_passed=10, tests_total=10)
        assert s.correctness == 1.0
        assert s.composite > 0.0

    def test_zero_correctness(self) -> None:
        """Test functionality: zero correctness."""
        scorer = OutcomeScorer()
        s = scorer.score(tests_passed=0, tests_total=10, tokens_used=1000)
        assert s.correctness == 0.0

    def test_efficiency(self) -> None:
        """Test functionality: efficiency."""
        scorer = OutcomeScorer()
        s = scorer.score(tokens_used=200, token_budget=1000)
        assert s.efficiency == 0.8

    def test_quality(self) -> None:
        """Test functionality: quality."""
        scorer = OutcomeScorer()
        s = scorer.score(quality_issues=3, max_quality_issues=10)
        assert s.quality == 0.7

    def test_to_dict(self) -> None:
        """Test functionality: to dict."""
        s = OutcomeScore(correctness=0.9, composite=0.85)
        d = s.to_dict()
        assert d["correctness"] == 0.9


# ── StrategyLibrary ──────────────────────────────────────────────


class TestStrategy:
    """Test suite for Strategy."""
    def test_record_outcome(self) -> None:
        """Test functionality: record outcome."""
        s = Strategy("fast")
        s.record_outcome(True)
        assert s.usage_count == 1
        assert s.success_rate == 1.0
        s.record_outcome(False)
        assert s.usage_count == 2

    def test_to_dict(self) -> None:
        """Test functionality: to dict."""
        s = Strategy("test", prompt_template="Do: {task}")
        assert s.to_dict()["name"] == "test"


class TestStrategyLibrary:
    """Test suite for StrategyLibrary."""
    def test_add_and_get(self) -> None:
        """Test functionality: add and get."""
        lib = StrategyLibrary()
        lib.add(Strategy("fast"))
        assert lib.get("fast") is not None
        assert lib.size == 1

    def test_remove(self) -> None:
        """Test functionality: remove."""
        lib = StrategyLibrary()
        lib.add(Strategy("fast"))
        assert lib.remove("fast") is True
        assert lib.size == 0

    def test_best_strategy(self) -> None:
        """Test functionality: best strategy."""
        lib = StrategyLibrary()
        low = Strategy("low", success_rate=0.3)
        high = Strategy("high", success_rate=0.9)
        lib.add(low)
        lib.add(high)
        assert lib.best_strategy() is not None
        assert lib.best_strategy().name == "high"

    def test_list_sorted(self) -> None:
        """Test functionality: list sorted."""
        lib = StrategyLibrary()
        lib.add(Strategy("a", success_rate=0.5))
        lib.add(Strategy("b", success_rate=0.9))
        ordered = lib.list_strategies()
        assert ordered[0].name == "b"


# ── ABTestEngine ─────────────────────────────────────────────────


class TestABTestEngine:
    """Test suite for ABEngine."""
    def test_clear_winner(self) -> None:
        """Test functionality: clear winner."""
        engine = ABTestEngine()
        result = engine.compare_scores("a", [0.9, 0.8, 0.85], "b", [0.5, 0.4, 0.3])
        assert result.winner == "a"
        assert result.wins_a == 3

    def test_tie(self) -> None:
        """Test functionality: tie."""
        engine = ABTestEngine()
        result = engine.compare_scores("a", [0.5], "b", [0.5])
        assert result.winner == "tie"

    def test_to_dict(self) -> None:
        """Test functionality: to dict."""
        r = ABTestResult(strategy_a="x", strategy_b="y", winner="x")
        d = r.to_dict()
        assert d["winner"] == "x"


# ── MetaAgent ────────────────────────────────────────────────────


class TestMetaAgent:
    """Test suite for MetaAgent."""
    def test_run_basic(self) -> None:
        """Test functionality: run basic."""
        meta = MetaAgent()
        meta.library.add(Strategy("fast", "go fast"))
        meta.library.add(Strategy("careful", "go careful"))

        def task_fn(strategy_name: str) -> dict:
            score = 0.9 if strategy_name == "fast" else 0.7
            return {"tests_passed": 9, "tests_total": 10, "tokens_used": 100}

        records = meta.run(task_fn, iterations=3)
        assert len(records) == 3
        assert len(meta.history) == 3

    def test_improvement_tracked(self) -> None:
        """Test functionality: improvement tracked."""
        meta = MetaAgent()
        meta.library.add(Strategy("s1"))
        counter = {"n": 0}

        def improving_task(name: str) -> dict:
            counter["n"] += 1
            return {"tests_passed": counter["n"], "tests_total": 10}

        meta.run(improving_task, iterations=5)
        # Later iterations should have higher scores
        assert meta.history[-1].score >= meta.history[0].score

    def test_no_strategies(self) -> None:
        """Test functionality: no strategies."""
        meta = MetaAgent()
        result = meta.run(lambda n: {}, iterations=3)
        assert len(result) == 0

    def test_task_failure_handled(self) -> None:
        """Test functionality: task failure handled."""
        meta = MetaAgent()
        meta.library.add(Strategy("bad"))

        def failing(name: str) -> dict:
            raise RuntimeError("boom")

        records = meta.run(failing, iterations=2)
        assert len(records) == 2
        assert records[0].score == 0.0
