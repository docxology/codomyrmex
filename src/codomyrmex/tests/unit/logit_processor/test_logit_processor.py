"""Unit tests for the logit_processor module."""

import numpy as np
import pytest

from codomyrmex.logit_processor import (
    LogitProcessorList,
    RepetitionPenaltyProcessor,
    TemperatureProcessor,
    TopKProcessor,
    TopPProcessor,
    greedy_decode,
    sample_token,
)


class TestTemperatureProcessor:
    @pytest.mark.unit
    def test_temperature_scales_logits(self):
        proc = TemperatureProcessor(temperature=2.0)
        logits = np.array([1.0, 2.0, 3.0])
        result = proc(logits)
        np.testing.assert_allclose(result, [0.5, 1.0, 1.5])

    @pytest.mark.unit
    def test_temperature_one_unchanged(self):
        proc = TemperatureProcessor(temperature=1.0)
        logits = np.array([1.0, 2.0, 3.0])
        np.testing.assert_allclose(proc(logits), logits)

    @pytest.mark.unit
    def test_low_temperature_sharpens(self):
        proc = TemperatureProcessor(temperature=0.1)
        logits = np.array([1.0, 2.0, 3.0])
        result = proc(logits)
        # Low temperature magnifies differences
        assert (result[2] - result[1]) > (logits[2] - logits[1])

    @pytest.mark.unit
    def test_invalid_temperature_zero_raises(self):
        with pytest.raises(ValueError, match="positive"):
            TemperatureProcessor(temperature=0.0)

    @pytest.mark.unit
    def test_invalid_temperature_negative_raises(self):
        with pytest.raises(ValueError, match="positive"):
            TemperatureProcessor(temperature=-1.0)


class TestTopKProcessor:
    @pytest.mark.unit
    def test_topk_zeros_non_top(self):
        proc = TopKProcessor(top_k=2)
        logits = np.array([1.0, 3.0, 2.0, 0.5])
        result = proc(logits)
        # Top-2 are indices 1 (3.0) and 2 (2.0)
        assert np.isfinite(result[1])  # 3.0 kept
        assert np.isfinite(result[2])  # 2.0 kept
        assert result[0] == float("-inf")
        assert result[3] == float("-inf")

    @pytest.mark.unit
    def test_topk_larger_than_vocab(self):
        proc = TopKProcessor(top_k=100)
        logits = np.array([1.0, 2.0, 3.0])
        result = proc(logits)
        # All should remain since k > vocab_size
        assert np.all(np.isfinite(result))

    @pytest.mark.unit
    def test_topk_one_keeps_only_max(self):
        proc = TopKProcessor(top_k=1)
        logits = np.array([1.0, 5.0, 2.0, 3.0])
        result = proc(logits)
        finite_count = np.sum(np.isfinite(result))
        assert finite_count == 1
        assert np.isfinite(result[1])  # Index of max kept

    @pytest.mark.unit
    def test_invalid_topk_raises(self):
        with pytest.raises(ValueError, match="positive"):
            TopKProcessor(top_k=0)

    @pytest.mark.unit
    def test_topk_preserves_values(self):
        proc = TopKProcessor(top_k=2)
        logits = np.array([1.0, 3.0, 2.0])
        result = proc(logits)
        # Values that are kept should be unchanged
        assert result[1] == 3.0
        assert result[2] == 2.0


class TestTopPProcessor:
    @pytest.mark.unit
    def test_topp_keeps_at_least_one(self):
        proc = TopPProcessor(top_p=0.0001)  # Very restrictive
        logits = np.array([10.0, 1.0, 1.0, 1.0])
        result = proc(logits)
        # At least one finite value remains
        assert np.any(np.isfinite(result))

    @pytest.mark.unit
    def test_topp_one_keeps_all(self):
        proc = TopPProcessor(top_p=1.0)
        logits = np.array([1.0, 2.0, 3.0])
        result = proc(logits)
        # All logits should remain finite
        assert np.all(np.isfinite(result))

    @pytest.mark.unit
    def test_topp_filters_low_prob_tokens(self):
        # One dominant token, rest very low
        logits = np.array([10.0, -10.0, -10.0, -10.0])
        proc = TopPProcessor(top_p=0.5)
        result = proc(logits)
        # Token 0 dominates, others should be filtered
        assert np.isfinite(result[0])

    @pytest.mark.unit
    def test_invalid_topp_zero_raises(self):
        with pytest.raises(ValueError, match="top_p"):
            TopPProcessor(top_p=0.0)

    @pytest.mark.unit
    def test_invalid_topp_over_one_raises(self):
        with pytest.raises(ValueError, match="top_p"):
            TopPProcessor(top_p=1.5)


class TestRepetitionPenalty:
    @pytest.mark.unit
    def test_penalty_reduces_positive_logits(self):
        proc = RepetitionPenaltyProcessor(penalty=2.0)
        logits = np.array([4.0, 2.0, 1.0])
        result = proc(logits, input_ids=[0])
        assert result[0] < logits[0]  # Token 0 was penalized
        assert result[1] == logits[1]  # Token 1 unchanged
        assert result[2] == logits[2]  # Token 2 unchanged

    @pytest.mark.unit
    def test_penalty_amplifies_negative_logits(self):
        proc = RepetitionPenaltyProcessor(penalty=2.0)
        logits = np.array([-2.0, 1.0])
        result = proc(logits, input_ids=[0])
        # Negative logit * penalty = more negative
        assert result[0] < logits[0]

    @pytest.mark.unit
    def test_no_penalty_with_no_input_ids(self):
        proc = RepetitionPenaltyProcessor(penalty=2.0)
        logits = np.array([1.0, 2.0, 3.0])
        result = proc(logits, input_ids=[])
        np.testing.assert_allclose(result, logits)

    @pytest.mark.unit
    def test_no_penalty_with_none_input_ids(self):
        proc = RepetitionPenaltyProcessor(penalty=2.0)
        logits = np.array([1.0, 2.0, 3.0])
        result = proc(logits, input_ids=None)
        np.testing.assert_allclose(result, logits)

    @pytest.mark.unit
    def test_out_of_range_ids_ignored(self):
        proc = RepetitionPenaltyProcessor(penalty=2.0)
        logits = np.array([1.0, 2.0])
        result = proc(logits, input_ids=[999])  # Out of range
        np.testing.assert_allclose(result, logits)

    @pytest.mark.unit
    def test_invalid_penalty_raises(self):
        with pytest.raises(ValueError, match="penalty"):
            RepetitionPenaltyProcessor(penalty=0.5)


class TestLogitProcessorList:
    @pytest.mark.unit
    def test_empty_list_returns_input(self):
        chain = LogitProcessorList([])
        logits = np.array([1.0, 2.0, 3.0])
        result = chain(logits)
        np.testing.assert_allclose(result, logits)

    @pytest.mark.unit
    def test_chained_processors(self):
        chain = LogitProcessorList([
            TemperatureProcessor(temperature=2.0),
            TopKProcessor(top_k=2),
        ])
        logits = np.array([1.0, 3.0, 2.0])
        result = chain(logits)
        # After temp: [0.5, 1.5, 1.0]; after top-k=2: keep indices 1,2
        assert result[0] == float("-inf")
        assert np.isfinite(result[1])
        assert np.isfinite(result[2])

    @pytest.mark.unit
    def test_append(self):
        chain = LogitProcessorList([])
        chain.append(TemperatureProcessor(temperature=2.0))
        logits = np.array([2.0, 4.0])
        result = chain(logits)
        np.testing.assert_allclose(result, [1.0, 2.0])


class TestSampleToken:
    @pytest.mark.unit
    def test_greedy_returns_argmax(self):
        logits = np.array([1.0, 5.0, 2.0, 0.1])
        assert greedy_decode(logits) == 1  # Index of max (5.0)

    @pytest.mark.unit
    def test_sample_deterministic_with_seed(self):
        logits = np.array([1.0, 2.0, 3.0, 1.0])
        t1 = sample_token(logits, seed=42)
        t2 = sample_token(logits, seed=42)
        assert t1 == t2

    @pytest.mark.unit
    def test_sample_returns_valid_index(self):
        logits = np.random.randn(100)
        for _ in range(20):
            token = sample_token(logits)
            assert 0 <= token < 100

    @pytest.mark.unit
    def test_sample_with_all_processors(self):
        logits = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        token = sample_token(
            logits,
            temperature=0.8,
            top_k=3,
            top_p=0.9,
            repetition_penalty=1.2,
            input_ids=[0, 1],
            seed=123,
        )
        assert 0 <= token < 5

    @pytest.mark.unit
    def test_sample_with_extreme_logits(self):
        # One very high logit should dominate
        logits = np.array([0.0, 0.0, 100.0, 0.0])
        token = sample_token(logits, seed=42)
        assert token == 2

    @pytest.mark.unit
    def test_greedy_with_ties(self):
        logits = np.array([5.0, 5.0, 1.0])
        result = greedy_decode(logits)
        assert result in [0, 1]  # Either max index is valid
