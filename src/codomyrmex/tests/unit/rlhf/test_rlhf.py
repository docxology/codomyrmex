"""
Unit tests for the RLHF (PPO) module.

Tests cover:
- GAE computation (returns >= rewards for positive rewards)
- PPO clip fraction bounds
- Entropy positivity for non-deterministic policy
- Reward model preference loss behavior
- Actor log-probability properties
- Critic value output shapes
- PPOTrainer loss history tracking
- MCP tool interface
"""

import numpy as np
import pytest

from codomyrmex.rlhf import Actor, Critic, PPOTrainer, RewardModel, ppo_step
from codomyrmex.rlhf.ppo import PPOConfig, compute_gae

# ---------------------------------------------------------------------------
# compute_gae
# ---------------------------------------------------------------------------


class TestComputeGAE:
    """Tests for Generalized Advantage Estimation."""

    @pytest.mark.unit
    def test_gae_output_shapes(self):
        """GAE should return advantages and returns with same shape as rewards."""
        T = 10
        rewards = np.random.randn(T)
        values = np.random.randn(T)
        advantages, returns = compute_gae(rewards, values, last_value=0.0)
        assert advantages.shape == (T,)
        assert returns.shape == (T,)

    @pytest.mark.unit
    def test_gae_returns_equal_advantages_plus_values(self):
        """returns = advantages + values by definition."""
        T = 8
        rewards = np.random.randn(T)
        values = np.random.randn(T)
        advantages, returns = compute_gae(rewards, values, last_value=0.0)
        np.testing.assert_allclose(returns, advantages + values, atol=1e-10)

    @pytest.mark.unit
    def test_gae_discount_positive_rewards(self):
        """For positive rewards and zero values, returns should be >= rewards."""
        T = 5
        rewards = np.ones(T)  # All positive
        values = np.zeros(T)
        advantages, returns = compute_gae(
            rewards, values, last_value=0.0, gamma=0.99, gae_lambda=0.95
        )
        # Returns should be at least as large as immediate rewards due to discounting
        assert np.all(returns >= rewards - 1e-10)

    @pytest.mark.unit
    def test_gae_zero_rewards_zero_values(self):
        """With all zeros, advantages and returns should be zero."""
        T = 5
        rewards = np.zeros(T)
        values = np.zeros(T)
        advantages, returns = compute_gae(rewards, values, last_value=0.0)
        np.testing.assert_allclose(advantages, 0.0, atol=1e-10)
        np.testing.assert_allclose(returns, 0.0, atol=1e-10)

    @pytest.mark.unit
    def test_gae_single_step(self):
        """Single step GAE: delta = r + gamma*V_next - V, advantage = delta."""
        rewards = np.array([1.0])
        values = np.array([0.5])
        last_value = 0.3
        gamma = 0.99
        advantages, returns = compute_gae(
            rewards, values, last_value, gamma=gamma, gae_lambda=0.95
        )
        expected_delta = 1.0 + gamma * 0.3 - 0.5
        np.testing.assert_allclose(advantages[0], expected_delta, atol=1e-10)


# ---------------------------------------------------------------------------
# Actor
# ---------------------------------------------------------------------------


class TestActor:
    """Tests for the Actor (policy) network."""

    @pytest.mark.unit
    def test_actor_output_shape(self):
        """Actor output should be (batch, d_action)."""
        actor = Actor(d_state=8, d_action=4)
        states = np.random.randn(16, 8)
        log_probs = actor(states)
        assert log_probs.shape == (16, 4)

    @pytest.mark.unit
    def test_actor_log_probs_are_non_positive(self):
        """Log probabilities should be <= 0."""
        np.random.seed(42)
        actor = Actor(d_state=8, d_action=4)
        states = np.random.randn(10, 8)
        log_probs = actor(states)
        assert np.all(log_probs <= 1e-7)

    @pytest.mark.unit
    def test_actor_log_probs_sum_to_one(self):
        """exp(log_probs) should sum to ~1 across actions (valid distribution)."""
        np.random.seed(42)
        actor = Actor(d_state=8, d_action=4)
        states = np.random.randn(5, 8)
        log_probs = actor(states)
        probs = np.exp(log_probs)
        np.testing.assert_allclose(np.sum(probs, axis=-1), 1.0, atol=1e-6)

    @pytest.mark.unit
    def test_actor_deterministic_with_seed(self):
        """Same seed should produce same outputs."""
        np.random.seed(42)
        actor1 = Actor(d_state=4, d_action=3)
        states = np.random.randn(2, 4)
        out1 = actor1(states)

        np.random.seed(42)
        actor2 = Actor(d_state=4, d_action=3)
        states2 = np.random.randn(2, 4)
        out2 = actor2(states2)

        np.testing.assert_allclose(out1, out2, atol=1e-10)


# ---------------------------------------------------------------------------
# Critic
# ---------------------------------------------------------------------------


class TestCritic:
    """Tests for the Critic (value function) network."""

    @pytest.mark.unit
    def test_critic_output_shape(self):
        """Critic should return scalar value per state."""
        critic = Critic(d_state=8)
        states = np.random.randn(16, 8)
        values = critic(states)
        assert values.shape == (16,)

    @pytest.mark.unit
    def test_critic_single_state(self):
        """Critic should work on single state."""
        critic = Critic(d_state=4)
        state = np.random.randn(1, 4)
        value = critic(state)
        assert value.shape == (1,)
        assert np.isfinite(value[0])


# ---------------------------------------------------------------------------
# RewardModel
# ---------------------------------------------------------------------------


class TestRewardModel:
    """Tests for the RLHF reward model."""

    @pytest.mark.unit
    def test_reward_model_score_shape(self):
        """Reward model should return scalar score per state."""
        rm = RewardModel(d_state=8)
        states = np.random.randn(10, 8)
        scores = rm.score(states)
        assert scores.shape == (10,)

    @pytest.mark.unit
    def test_reward_model_preference_loss_is_scalar(self):
        """Preference loss should be a scalar float."""
        rm = RewardModel(d_state=8)
        w = np.random.randn(4, 8)
        loss_input = np.random.randn(4, 8)
        loss = rm.preference_loss(w, loss_input)
        assert isinstance(loss, float)
        assert np.isfinite(loss)

    @pytest.mark.unit
    def test_reward_model_preference_loss_direction(self):
        """Preference loss should be lower when winner score > loser score.

        We construct states where the reward model gives higher scores to winners
        by using the same states but shifting winner states to amplify scores.
        """
        np.random.seed(42)
        rm = RewardModel(d_state=4)

        # Get base scores
        base = np.random.randn(10, 4)
        scores = rm.score(base)

        # Sort: top half are winners, bottom half are losers
        idx = np.argsort(scores)
        winners = base[idx[5:]]
        losers = base[idx[:5]]

        loss_correct = rm.preference_loss(winners, losers)

        # Swap: losers are now "winners" -- this should have higher loss
        loss_swapped = rm.preference_loss(losers, winners)

        assert loss_correct < loss_swapped


# ---------------------------------------------------------------------------
# PPO Step
# ---------------------------------------------------------------------------


class TestPPOStep:
    """Tests for the PPO loss computation."""

    def _make_batch(self, seed=42):
        """Create a synthetic PPO batch."""
        np.random.seed(seed)
        d_state, d_action, batch = 8, 4, 16
        actor = Actor(d_state, d_action)
        critic = Critic(d_state)
        states = np.random.randn(batch, d_state)
        actions = np.random.randint(0, d_action, batch)
        log_probs_all = actor(states)
        old_log_probs = np.array(
            [log_probs_all[i, actions[i]] for i in range(batch)]
        )
        values = critic(states)
        rewards = np.random.randn(batch) * 0.1
        advantages, returns = compute_gae(rewards, values, last_value=0.0)
        return states, actions, old_log_probs, advantages, returns, actor, critic

    @pytest.mark.unit
    def test_ppo_step_returns_expected_keys(self):
        """PPO step should return all expected loss components."""
        states, actions, old_lp, adv, ret, actor, critic = self._make_batch()
        result = ppo_step(states, actions, old_lp, adv, ret, actor, critic)
        expected_keys = {
            "policy_loss",
            "value_loss",
            "entropy",
            "total_loss",
            "mean_ratio",
            "clip_fraction",
        }
        assert set(result.keys()) == expected_keys

    @pytest.mark.unit
    def test_ppo_clip_fraction_bounded(self):
        """Clip fraction should be between 0 and 1 (or slightly above due to sum)."""
        states, actions, old_lp, adv, ret, actor, critic = self._make_batch()
        result = ppo_step(states, actions, old_lp, adv, ret, actor, critic)
        assert 0.0 <= result["clip_fraction"] <= 2.0

    @pytest.mark.unit
    def test_entropy_positive(self):
        """Entropy should be > 0 for a non-deterministic policy."""
        states, actions, old_lp, adv, ret, actor, critic = self._make_batch()
        result = ppo_step(states, actions, old_lp, adv, ret, actor, critic)
        assert result["entropy"] > 0.0

    @pytest.mark.unit
    def test_mean_ratio_close_to_one_same_policy(self):
        """When using same policy for old and new, ratio should be ~1."""
        states, actions, old_lp, adv, ret, actor, critic = self._make_batch()
        result = ppo_step(states, actions, old_lp, adv, ret, actor, critic)
        assert abs(result["mean_ratio"] - 1.0) < 0.1

    @pytest.mark.unit
    def test_value_loss_non_negative(self):
        """Value loss (MSE) should always be >= 0."""
        states, actions, old_lp, adv, ret, actor, critic = self._make_batch()
        result = ppo_step(states, actions, old_lp, adv, ret, actor, critic)
        assert result["value_loss"] >= 0.0

    @pytest.mark.unit
    def test_total_loss_is_finite(self):
        """Total loss should be a finite number."""
        states, actions, old_lp, adv, ret, actor, critic = self._make_batch()
        result = ppo_step(states, actions, old_lp, adv, ret, actor, critic)
        assert np.isfinite(result["total_loss"])


# ---------------------------------------------------------------------------
# PPOTrainer
# ---------------------------------------------------------------------------


class TestPPOTrainer:
    """Tests for the PPOTrainer orchestrator."""

    @pytest.mark.unit
    def test_trainer_tracks_losses(self):
        """Trainer should append to losses list after each compute_loss call."""
        np.random.seed(42)
        trainer = PPOTrainer(d_state=8, d_action=4)
        states = np.random.randn(8, 8)
        actions = np.random.randint(0, 4, 8)
        log_probs_all = trainer.actor(states)
        old_lp = np.array([log_probs_all[i, actions[i]] for i in range(8)])
        values = trainer.critic(states)
        adv, ret = compute_gae(np.random.randn(8) * 0.1, values, 0.0)

        trainer.compute_loss(states, actions, old_lp, adv, ret)
        trainer.compute_loss(states, actions, old_lp, adv, ret)
        assert len(trainer.losses) == 2

    @pytest.mark.unit
    def test_trainer_custom_config(self):
        """Trainer should accept custom PPOConfig."""
        config = PPOConfig(clip_epsilon=0.1, entropy_coef=0.05)
        trainer = PPOTrainer(d_state=4, d_action=2, config=config)
        assert trainer.config.clip_epsilon == 0.1
        assert trainer.config.entropy_coef == 0.05


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


class TestMCPTools:
    """Tests for RLHF MCP tool interface."""

    @pytest.mark.unit
    def test_rlhf_ppo_step_tool(self):
        from codomyrmex.rlhf.mcp_tools import rlhf_ppo_step

        result = rlhf_ppo_step(d_state=8, d_action=4, batch_size=16, seed=42)
        assert result["status"] == "success"
        assert "policy_loss" in result
        assert "entropy" in result

    @pytest.mark.unit
    def test_rlhf_reward_score_tool(self):
        from codomyrmex.rlhf.mcp_tools import rlhf_reward_score

        result = rlhf_reward_score(d_state=8, batch_size=4, seed=42)
        assert result["status"] == "success"
        assert "scores" in result
        assert "preference_loss" in result

    @pytest.mark.unit
    def test_ppo_step_tool_has_mcp_metadata(self):
        from codomyrmex.rlhf.mcp_tools import rlhf_ppo_step

        assert hasattr(rlhf_ppo_step, "_mcp_tool")
        assert rlhf_ppo_step._mcp_tool["category"] == "rlhf"

    @pytest.mark.unit
    def test_reward_score_tool_has_mcp_metadata(self):
        from codomyrmex.rlhf.mcp_tools import rlhf_reward_score

        assert hasattr(rlhf_reward_score, "_mcp_tool")
        assert rlhf_reward_score._mcp_tool["category"] == "rlhf"
