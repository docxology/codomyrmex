"""MCP tools for the DPO module."""

import numpy as np

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="dpo")
def dpo_compute_loss(
    beta: float = 0.1,
    batch_size: int = 4,
    seed: int = 42,
) -> dict:
    """Compute DPO loss on synthetic preference data.

    Args:
        beta: KL penalty coefficient (typical range 0.01-0.5)
        batch_size: Number of preference pairs
        seed: Random seed for reproducibility

    Returns:
        dict with: loss, accuracy, rewards_w mean, rewards_l mean
    """
    from .loss import compute_dpo_loss

    np.random.seed(seed)

    # Simulate log probs: winner should have higher policy/ref ratio
    policy_w = np.random.randn(batch_size) * 0.5 - 1.0  # winner log probs
    policy_l = np.random.randn(batch_size) * 0.5 - 2.0  # loser (lower)
    ref_w = policy_w + np.random.randn(batch_size) * 0.1  # ref ~ policy
    ref_l = policy_l + np.random.randn(batch_size) * 0.1

    result = compute_dpo_loss(policy_w, policy_l, ref_w, ref_l, beta=beta)
    result["status"] = "success"
    return result
