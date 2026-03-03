"""MCP tools for the RLHF module."""

from typing import Any

import numpy as np

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="rlhf")
def rlhf_ppo_step(
    d_state: int = 8,
    d_action: int = 4,
    batch_size: int = 16,
    seed: int = 42,
) -> dict[str, Any]:
    """Run a single PPO step on synthetic data and return loss metrics.

    Args:
        d_state: State dimension
        d_action: Number of discrete actions
        batch_size: Number of transitions in the batch
        seed: Random seed for reproducibility

    Returns:
        dict with: policy_loss, value_loss, entropy, total_loss, mean_ratio, clip_fraction

    """
    from .ppo import PPOTrainer, compute_gae

    np.random.seed(seed)

    trainer = PPOTrainer(d_state, d_action)

    # Generate synthetic rollout
    states = np.random.randn(batch_size, d_state)
    actions = np.random.randint(0, d_action, batch_size)
    rewards = np.random.randn(batch_size) * 0.1

    # Get old log probs and values
    old_log_probs_all = trainer.actor(states)
    old_log_probs = np.array(
        [old_log_probs_all[i, actions[i]] for i in range(batch_size)]
    )
    values = trainer.critic(states)

    # Compute GAE
    advantages, returns = compute_gae(rewards, values, last_value=0.0)

    result = trainer.compute_loss(states, actions, old_log_probs, advantages, returns)
    result["status"] = "success"
    return result


@mcp_tool(category="rlhf")
def rlhf_reward_score(
    d_state: int = 8,
    batch_size: int = 4,
    seed: int = 42,
) -> dict[str, Any]:
    """Score synthetic states using the RLHF reward model.

    Args:
        d_state: State/response embedding dimension
        batch_size: Number of samples to score
        seed: Random seed for reproducibility

    Returns:
        dict with: scores (list), preference_loss, mean_score

    """
    from .ppo import RewardModel

    np.random.seed(seed)

    reward_model = RewardModel(d_state)
    states = np.random.randn(batch_size, d_state)
    scores = reward_model.score(states)

    # Also compute preference loss between first and second half
    half = batch_size // 2
    if half > 0:
        w_states = states[:half]
        l_states = states[half : 2 * half]
        pref_loss = reward_model.preference_loss(w_states, l_states)
    else:
        pref_loss = 0.0

    return {
        "scores": scores.tolist(),
        "preference_loss": float(pref_loss),
        "mean_score": float(np.mean(scores)),
        "status": "success",
    }
