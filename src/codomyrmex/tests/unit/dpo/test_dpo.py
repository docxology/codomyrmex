"""
Unit tests for the DPO (Direct Preference Optimization) module.

Tests cover:
- Log probability computation from logits
- DPO loss formula correctness (manual vs computed)
- Loss behavior when winner is better
- Perfect accuracy when rewards_w > rewards_l always
- DPOLoss stateful class and history tracking
- MCP tool interface
"""

import numpy as np
import pytest

from codomyrmex.dpo import DPOLoss, compute_dpo_loss, compute_log_probs


# ---------------------------------------------------------------------------
# compute_log_probs
# ---------------------------------------------------------------------------


class TestComputeLogProbs:
    """Tests for log probability computation from logits."""

    @pytest.mark.unit
    def test_log_probs_shape(self):
        batch, seq, vocab = 2, 5, 10
        logits = np.random.randn(batch, seq, vocab)
        labels = np.random.randint(0, vocab, (batch, seq))
        log_probs = compute_log_probs(logits, labels)
        assert log_probs.shape == (batch, seq)

    @pytest.mark.unit
    def test_log_probs_are_non_positive(self):
        """Log probabilities should be <= 0."""
        batch, seq, vocab = 3, 4, 8
        logits = np.random.randn(batch, seq, vocab)
        labels = np.random.randint(0, vocab, (batch, seq))
        log_probs = compute_log_probs(logits, labels)
        assert np.all(log_probs <= 0.0 + 1e-7)

    @pytest.mark.unit
    def test_ignore_index_gives_zero(self):
        """Tokens with ignore_index should have log_prob = 0."""
        logits = np.random.randn(1, 3, 5)
        labels = np.array([[2, -100, 4]])
        log_probs = compute_log_probs(logits, labels, ignore_index=-100)
        assert log_probs[0, 1] == 0.0

    @pytest.mark.unit
    def test_high_logit_gives_high_log_prob(self):
        """A token with a very high logit should have log_prob close to 0."""
        logits = np.zeros((1, 1, 5))
        logits[0, 0, 3] = 100.0  # Make token 3 dominant
        labels = np.array([[3]])
        log_probs = compute_log_probs(logits, labels)
        assert log_probs[0, 0] > -0.01  # Very close to 0


# ---------------------------------------------------------------------------
# compute_dpo_loss
# ---------------------------------------------------------------------------


class TestComputeDPOLoss:
    """Tests for the DPO loss function."""

    @pytest.mark.unit
    def test_loss_formula_correct(self):
        """Manual calculation vs compute_dpo_loss."""
        np.random.seed(42)
        batch = 4
        policy_w = np.array([1.0, 2.0, 1.5, 0.5])
        policy_l = np.array([0.5, 1.0, 0.5, 0.0])
        ref_w = np.array([0.8, 1.8, 1.3, 0.3])
        ref_l = np.array([0.4, 0.8, 0.4, -0.1])
        beta = 0.1

        # Manual computation
        rewards_w = beta * (policy_w - ref_w)
        rewards_l = beta * (policy_l - ref_l)
        logits = rewards_w - rewards_l
        expected_loss = -np.mean(np.log(1.0 / (1.0 + np.exp(-logits)) + 1e-9))

        result = compute_dpo_loss(policy_w, policy_l, ref_w, ref_l, beta=beta)
        np.testing.assert_allclose(result["loss"], expected_loss, atol=1e-10)

    @pytest.mark.unit
    def test_loss_decreases_with_better_winner(self):
        """When policy strongly prefers winner, loss should be lower."""
        batch = 8
        ref_w = np.zeros(batch)
        ref_l = np.zeros(batch)
        policy_l = np.zeros(batch)

        # Weak preference for winner
        policy_w_weak = np.ones(batch) * 0.5
        result_weak = compute_dpo_loss(
            policy_w_weak, policy_l, ref_w, ref_l, beta=0.1
        )

        # Strong preference for winner
        policy_w_strong = np.ones(batch) * 5.0
        result_strong = compute_dpo_loss(
            policy_w_strong, policy_l, ref_w, ref_l, beta=0.1
        )

        assert result_strong["loss"] < result_weak["loss"]

    @pytest.mark.unit
    def test_accuracy_perfect_when_winner_always_better(self):
        """If rewards_w > rewards_l for all samples, accuracy = 1.0."""
        batch = 10
        # Ensure policy strongly favors winner over reference
        policy_w = np.ones(batch) * 5.0
        policy_l = np.ones(batch) * -5.0
        ref_w = np.zeros(batch)
        ref_l = np.zeros(batch)

        result = compute_dpo_loss(policy_w, policy_l, ref_w, ref_l, beta=0.1)
        assert result["accuracy"] == 1.0

    @pytest.mark.unit
    def test_accuracy_zero_when_loser_always_preferred(self):
        """If rewards_l > rewards_w for all samples, accuracy = 0.0."""
        batch = 10
        policy_w = np.ones(batch) * -5.0
        policy_l = np.ones(batch) * 5.0
        ref_w = np.zeros(batch)
        ref_l = np.zeros(batch)

        result = compute_dpo_loss(policy_w, policy_l, ref_w, ref_l, beta=0.1)
        assert result["accuracy"] == 0.0

    @pytest.mark.unit
    def test_result_contains_expected_keys(self):
        result = compute_dpo_loss(
            np.array([1.0]), np.array([0.0]),
            np.array([0.5]), np.array([0.5]),
            beta=0.1,
        )
        assert "loss" in result
        assert "rewards_w" in result
        assert "rewards_l" in result
        assert "accuracy" in result
        assert "beta" in result

    @pytest.mark.unit
    def test_beta_stored_in_result(self):
        result = compute_dpo_loss(
            np.array([1.0]), np.array([0.0]),
            np.array([0.5]), np.array([0.5]),
            beta=0.25,
        )
        assert result["beta"] == 0.25


# ---------------------------------------------------------------------------
# DPOLoss stateful class
# ---------------------------------------------------------------------------


class TestDPOLoss:
    """Tests for the DPOLoss stateful wrapper."""

    @pytest.mark.unit
    def test_history_tracking(self):
        loss_fn = DPOLoss(beta=0.1)
        p_w = np.array([1.0, 2.0])
        p_l = np.array([0.0, 0.5])
        r_w = np.zeros(2)
        r_l = np.zeros(2)

        loss_fn(p_w, p_l, r_w, r_l)
        loss_fn(p_w, p_l, r_w, r_l)
        assert len(loss_fn.history) == 2

    @pytest.mark.unit
    def test_reset_clears_history(self):
        loss_fn = DPOLoss(beta=0.1)
        p_w = np.array([1.0])
        p_l = np.array([0.0])
        r_w = np.zeros(1)
        r_l = np.zeros(1)

        loss_fn(p_w, p_l, r_w, r_l)
        assert len(loss_fn.history) == 1
        loss_fn.reset()
        assert len(loss_fn.history) == 0

    @pytest.mark.unit
    def test_callable_returns_dict(self):
        loss_fn = DPOLoss(beta=0.1)
        result = loss_fn(
            np.array([1.0]), np.array([0.0]),
            np.array([0.5]), np.array([0.5]),
        )
        assert isinstance(result, dict)
        assert "loss" in result


# ---------------------------------------------------------------------------
# MCP tool
# ---------------------------------------------------------------------------


class TestMCPTool:
    """Tests for DPO MCP tool interface."""

    @pytest.mark.unit
    def test_dpo_compute_loss_tool(self):
        from codomyrmex.dpo.mcp_tools import dpo_compute_loss

        result = dpo_compute_loss(beta=0.1, batch_size=4, seed=42)
        assert result["status"] == "success"
        assert "loss" in result
        assert "accuracy" in result

    @pytest.mark.unit
    def test_dpo_tool_has_mcp_metadata(self):
        from codomyrmex.dpo.mcp_tools import dpo_compute_loss

        assert hasattr(dpo_compute_loss, "_mcp_tool")
        assert dpo_compute_loss._mcp_tool["category"] == "dpo"
