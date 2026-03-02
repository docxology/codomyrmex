"""
Unit tests for the LLM Eval Harness module.

Tests cover:
- ExactMatch metric scoring
- F1 metric scoring
- normalize_answer function
- EvalHarness with identity model
- EvalHarness with custom model function
- EvalTask and EvalResult dataclasses
- evaluate_all summary
- MCP tool interface
"""

import numpy as np
import pytest

from codomyrmex.eval_harness import (
    EvalHarness,
    EvalResult,
    EvalTask,
    ExactMatchMetric,
    F1Metric,
)
from codomyrmex.eval_harness.harness import normalize_answer

# ---------------------------------------------------------------------------
# normalize_answer
# ---------------------------------------------------------------------------


class TestNormalizeAnswer:
    """Tests for text normalization."""

    @pytest.mark.unit
    def test_strips_whitespace(self):
        assert normalize_answer("  hello  ") == "hello"

    @pytest.mark.unit
    def test_lowercases(self):
        assert normalize_answer("Hello World") == "hello world"

    @pytest.mark.unit
    def test_combined(self):
        assert normalize_answer("  HELLO  ") == "hello"

    @pytest.mark.unit
    def test_empty_string(self):
        assert normalize_answer("") == ""

    @pytest.mark.unit
    def test_already_normalized(self):
        assert normalize_answer("hello") == "hello"


# ---------------------------------------------------------------------------
# ExactMatchMetric
# ---------------------------------------------------------------------------


class TestExactMatchMetric:
    """Tests for exact match scoring."""

    @pytest.mark.unit
    def test_perfect_match(self):
        score = ExactMatchMetric.score(["hello", "world"], ["hello", "world"])
        assert score == 1.0

    @pytest.mark.unit
    def test_no_match(self):
        score = ExactMatchMetric.score(["foo", "bar"], ["baz", "qux"])
        assert score == 0.0

    @pytest.mark.unit
    def test_partial_match(self):
        score = ExactMatchMetric.score(["hello", "wrong"], ["hello", "right"])
        assert score == 0.5

    @pytest.mark.unit
    def test_case_insensitive(self):
        score = ExactMatchMetric.score(["Hello"], ["hello"])
        assert score == 1.0

    @pytest.mark.unit
    def test_whitespace_insensitive(self):
        score = ExactMatchMetric.score(["  hello  "], ["hello"])
        assert score == 1.0

    @pytest.mark.unit
    def test_empty_targets(self):
        score = ExactMatchMetric.score([], [])
        assert score == 0.0


# ---------------------------------------------------------------------------
# F1Metric
# ---------------------------------------------------------------------------


class TestF1Metric:
    """Tests for token-level F1 scoring."""

    @pytest.mark.unit
    def test_perfect_f1(self):
        score = F1Metric.score(["hello world"], ["hello world"])
        assert score == 1.0

    @pytest.mark.unit
    def test_zero_f1_no_overlap(self):
        score = F1Metric.score(["foo bar"], ["baz qux"])
        assert score == 0.0

    @pytest.mark.unit
    def test_partial_overlap(self):
        """Partial token overlap should give F1 between 0 and 1."""
        score = F1Metric.score(["hello world foo"], ["hello world bar"])
        assert 0.0 < score < 1.0

    @pytest.mark.unit
    def test_f1_single_perfect(self):
        """Single token perfect match."""
        f1 = F1Metric._f1_single("hello", "hello")
        assert f1 == 1.0

    @pytest.mark.unit
    def test_f1_single_no_match(self):
        """Single token pair with no overlap."""
        f1 = F1Metric._f1_single("foo", "bar")
        assert f1 == 0.0

    @pytest.mark.unit
    def test_f1_empty_prediction(self):
        """Empty prediction against non-empty target."""
        f1 = F1Metric._f1_single("", "hello")
        assert f1 == 0.0

    @pytest.mark.unit
    def test_f1_both_empty(self):
        """Both empty should be perfect match."""
        f1 = F1Metric._f1_single("", "")
        assert f1 == 1.0

    @pytest.mark.unit
    def test_f1_case_insensitive(self):
        score = F1Metric.score(["Hello World"], ["hello world"])
        assert score == 1.0

    @pytest.mark.unit
    def test_empty_targets(self):
        score = F1Metric.score([], [])
        assert score == 0.0


# ---------------------------------------------------------------------------
# EvalTask and EvalResult
# ---------------------------------------------------------------------------


class TestEvalDataclasses:
    """Tests for EvalTask and EvalResult dataclasses."""

    @pytest.mark.unit
    def test_eval_task_defaults(self):
        task = EvalTask(name="test", examples=[])
        assert task.metric == "exact_match"
        assert task.description == ""

    @pytest.mark.unit
    def test_eval_result_fields(self):
        result = EvalResult(
            task_name="test",
            num_examples=5,
            score=0.8,
            metric="exact_match",
            latency_ms_mean=1.5,
        )
        assert result.task_name == "test"
        assert result.num_examples == 5
        assert result.score == 0.8
        assert result.details == []


# ---------------------------------------------------------------------------
# EvalHarness
# ---------------------------------------------------------------------------


class TestEvalHarness:
    """Tests for the evaluation harness orchestrator."""

    @pytest.mark.unit
    def test_identity_model_exact_match(self):
        """Identity model should get 100% on exact_match when input==target."""
        harness = EvalHarness()  # identity model
        task = EvalTask(
            name="identity",
            examples=[
                {"input": "hello", "target": "hello"},
                {"input": "world", "target": "world"},
            ],
        )
        result = harness.evaluate_task(task)
        assert result.score == 1.0

    @pytest.mark.unit
    def test_identity_model_case_insensitive_match(self):
        """Identity model returns 'Hello', target is 'hello' -- should still match."""
        harness = EvalHarness()
        task = EvalTask(
            name="case",
            examples=[{"input": "Hello", "target": "hello"}],
        )
        result = harness.evaluate_task(task)
        assert result.score == 1.0

    @pytest.mark.unit
    def test_custom_model_function(self):
        """Custom model function should be used for predictions."""
        harness = EvalHarness(model_fn=lambda x: "always_this")
        task = EvalTask(
            name="custom",
            examples=[
                {"input": "q1", "target": "always_this"},
                {"input": "q2", "target": "something_else"},
            ],
        )
        result = harness.evaluate_task(task)
        assert result.score == 0.5

    @pytest.mark.unit
    def test_evaluate_task_returns_eval_result(self):
        harness = EvalHarness()
        task = EvalTask(name="test", examples=[{"input": "a", "target": "a"}])
        result = harness.evaluate_task(task)
        assert isinstance(result, EvalResult)

    @pytest.mark.unit
    def test_evaluate_task_tracks_latency(self):
        """Latency should be a positive number."""
        harness = EvalHarness()
        task = EvalTask(name="test", examples=[{"input": "a", "target": "a"}])
        result = harness.evaluate_task(task)
        assert result.latency_ms_mean >= 0.0

    @pytest.mark.unit
    def test_evaluate_task_details_populated(self):
        """Details should contain per-example results."""
        harness = EvalHarness()
        task = EvalTask(
            name="test",
            examples=[
                {"input": "a", "target": "a"},
                {"input": "b", "target": "c"},
            ],
        )
        result = harness.evaluate_task(task)
        assert len(result.details) == 2
        assert result.details[0]["correct"] is True
        assert result.details[1]["correct"] is False

    @pytest.mark.unit
    def test_evaluate_task_f1_metric(self):
        """Should use F1 metric when specified."""
        harness = EvalHarness()
        task = EvalTask(
            name="f1_test",
            examples=[{"input": "hello world", "target": "hello world"}],
            metric="f1",
        )
        result = harness.evaluate_task(task)
        assert result.metric == "f1"
        assert result.score == 1.0

    @pytest.mark.unit
    def test_evaluate_all_summary(self):
        """evaluate_all should return summary dict with all tasks."""
        harness = EvalHarness()
        tasks = [
            EvalTask(
                name="t1",
                examples=[{"input": "a", "target": "a"}],
            ),
            EvalTask(
                name="t2",
                examples=[
                    {"input": "b", "target": "b"},
                    {"input": "c", "target": "x"},
                ],
            ),
        ]
        summary = harness.evaluate_all(tasks)
        assert summary["num_tasks"] == 2
        assert len(summary["results"]) == 2
        # t1 = 1.0, t2 = 0.5, mean = 0.75
        np.testing.assert_allclose(summary["mean_score"], 0.75, atol=1e-10)

    @pytest.mark.unit
    def test_harness_accumulates_results(self):
        """Harness should accumulate results across evaluate_task calls."""
        harness = EvalHarness()
        task = EvalTask(name="test", examples=[{"input": "a", "target": "a"}])
        harness.evaluate_task(task)
        harness.evaluate_task(task)
        assert len(harness.results) == 2


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


class TestMCPTools:
    """Tests for Eval Harness MCP tool interface."""

    @pytest.mark.unit
    def test_eval_harness_run_tool(self):
        from codomyrmex.eval_harness.mcp_tools import eval_harness_run

        result = eval_harness_run()
        assert result["status"] == "success"
        assert "num_tasks" in result
        assert "mean_score" in result

    @pytest.mark.unit
    def test_eval_harness_score_tool(self):
        from codomyrmex.eval_harness.mcp_tools import eval_harness_score

        result = eval_harness_score(
            predictions=["hello", "world"],
            targets=["hello", "world"],
            metric="exact_match",
        )
        assert result["status"] == "success"
        assert result["score"] == 1.0

    @pytest.mark.unit
    def test_eval_harness_score_f1(self):
        from codomyrmex.eval_harness.mcp_tools import eval_harness_score

        result = eval_harness_score(
            predictions=["hello world"],
            targets=["hello world"],
            metric="f1",
        )
        assert result["score"] == 1.0

    @pytest.mark.unit
    def test_eval_harness_run_has_mcp_metadata(self):
        from codomyrmex.eval_harness.mcp_tools import eval_harness_run

        assert hasattr(eval_harness_run, "_mcp_tool")
        assert eval_harness_run._mcp_tool["category"] == "eval_harness"

    @pytest.mark.unit
    def test_eval_harness_score_has_mcp_metadata(self):
        from codomyrmex.eval_harness.mcp_tools import eval_harness_score

        assert hasattr(eval_harness_score, "_mcp_tool")
        assert eval_harness_score._mcp_tool["category"] == "eval_harness"
