"""
Unit tests for model_ops.evaluation.evaluators — Zero-Mock compliant.

Covers: Evaluator, exact_match_metric, length_ratio_metric.
"""

import pytest

from codomyrmex.model_ops.evaluation.evaluators import (
    Evaluator,
    exact_match_metric,
    length_ratio_metric,
)

# ── exact_match_metric ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestExactMatchMetric:
    def test_exact_match_returns_one(self):
        assert exact_match_metric("hello", "hello") == 1.0

    def test_mismatch_returns_zero(self):
        assert exact_match_metric("hello", "world") == 0.0

    def test_whitespace_stripped(self):
        assert exact_match_metric("  hello  ", "hello") == 1.0

    def test_case_sensitive(self):
        assert exact_match_metric("Hello", "hello") == 0.0

    def test_empty_strings_match(self):
        assert exact_match_metric("", "") == 1.0


# ── length_ratio_metric ───────────────────────────────────────────────────


@pytest.mark.unit
class TestLengthRatioMetric:
    def test_equal_length_returns_one(self):
        assert length_ratio_metric("abcde", "12345") == 1.0

    def test_double_length_returns_two(self):
        assert length_ratio_metric("aabbcc", "abc") == 2.0

    def test_half_length_returns_half(self):
        assert length_ratio_metric("ab", "abcd") == 0.5

    def test_empty_reference_returns_one(self):
        # Zero-length ref → guard returns 1.0
        assert length_ratio_metric("anything", "") == 1.0

    def test_empty_pred_non_empty_ref(self):
        assert length_ratio_metric("", "abc") == 0.0


# ── Evaluator ─────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestEvaluator:
    def test_evaluate_exact_match(self):
        ev = Evaluator({"exact": exact_match_metric})
        results = ev.evaluate(["a", "b", "c"], ["a", "x", "c"])
        # 2 out of 3 match → 2/3 ≈ 0.667
        assert abs(results["exact"] - 2 / 3) < 1e-9

    def test_evaluate_all_correct(self):
        ev = Evaluator({"exact": exact_match_metric})
        results = ev.evaluate(["a", "b"], ["a", "b"])
        assert results["exact"] == 1.0

    def test_evaluate_none_correct(self):
        ev = Evaluator({"exact": exact_match_metric})
        results = ev.evaluate(["x", "y"], ["a", "b"])
        assert results["exact"] == 0.0

    def test_evaluate_multiple_metrics(self):
        ev = Evaluator({
            "exact": exact_match_metric,
            "ratio": length_ratio_metric,
        })
        results = ev.evaluate(["hello"], ["hello"])
        assert "exact" in results
        assert "ratio" in results
        assert results["exact"] == 1.0
        assert results["ratio"] == 1.0

    def test_evaluate_length_mismatch_raises(self):
        ev = Evaluator({"exact": exact_match_metric})
        with pytest.raises(ValueError, match="same length"):
            ev.evaluate(["a", "b"], ["a"])

    def test_evaluate_empty_lists_returns_zero(self):
        ev = Evaluator({"exact": exact_match_metric})
        results = ev.evaluate([], [])
        assert results["exact"] == 0.0

    def test_custom_metric_function(self):
        def always_half(pred, ref):
            return 0.5

        ev = Evaluator({"custom": always_half})
        results = ev.evaluate(["any", "thing"], ["a", "b"])
        assert results["custom"] == 0.5
