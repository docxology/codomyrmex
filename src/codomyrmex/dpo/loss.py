"""
DPO (Direct Preference Optimization) loss implementation.

Implements the DPO loss from Rafailov et al. (2023). DPO directly optimizes
a language model policy from human preferences without fitting a separate
reward model.

Pure Python + NumPy. No PyTorch dependency.
"""

import numpy as np
from typing import Optional


def compute_log_probs(
    logits: np.ndarray,
    labels: np.ndarray,
    ignore_index: int = -100,
) -> np.ndarray:
    """
    Compute per-token log probabilities from logits.

    Args:
        logits: (batch, seq, vocab_size) raw model outputs
        labels: (batch, seq) token IDs to compute probs for
        ignore_index: Token ID to ignore in the calculation

    Returns:
        log_probs: (batch, seq) log probabilities, 0 for ignored tokens
    """
    batch, seq, vocab = logits.shape

    # Numerically stable log-softmax
    logits_max = np.max(logits, axis=-1, keepdims=True)
    log_probs_all = logits - logits_max - np.log(
        np.sum(np.exp(logits - logits_max), axis=-1, keepdims=True) + 1e-9
    )

    # Gather log probs at label positions
    log_probs = np.zeros((batch, seq))
    for b in range(batch):
        for t in range(seq):
            if labels[b, t] != ignore_index:
                log_probs[b, t] = log_probs_all[b, t, labels[b, t]]

    return log_probs


def compute_dpo_loss(
    policy_log_probs_w: np.ndarray,  # Policy log probs on winner
    policy_log_probs_l: np.ndarray,  # Policy log probs on loser
    ref_log_probs_w: np.ndarray,  # Reference log probs on winner
    ref_log_probs_l: np.ndarray,  # Reference log probs on loser
    beta: float = 0.1,
) -> dict:
    """
    DPO loss (Rafailov et al. 2023).

    DPO directly optimizes the policy without a separate reward model.

    Loss = -log(sigmoid(beta * (log_pi_w - log_pi_l - log_ref_w + log_ref_l)))
         = -log(sigmoid(beta * (pi_ratio_w - pi_ratio_l)))

    where:
        pi_ratio_w = log_pi(y_w | x) - log_ref(y_w | x)  (advantage of winner)
        pi_ratio_l = log_pi(y_l | x) - log_ref(y_l | x)  (advantage of loser)

    Args:
        policy_log_probs_w: (batch,) sum of token log probs for winning response
        policy_log_probs_l: (batch,) for losing response
        ref_log_probs_w: (batch,) reference model log probs for winner
        ref_log_probs_l: (batch,) for loser
        beta: KL penalty coefficient (higher = more conservative)

    Returns:
        dict with: loss (scalar), rewards_w, rewards_l, accuracy
    """
    # Log ratios: implicit reward = beta * (policy - reference)
    rewards_w = beta * (policy_log_probs_w - ref_log_probs_w)
    rewards_l = beta * (policy_log_probs_l - ref_log_probs_l)

    # DPO loss: -E[log sigmoid(reward_w - reward_l)]
    logits = rewards_w - rewards_l
    loss = -np.mean(np.log(1.0 / (1.0 + np.exp(-logits)) + 1e-9))

    # Accuracy: fraction where winner is preferred
    accuracy = float(np.mean(rewards_w > rewards_l))

    return {
        "loss": float(loss),
        "rewards_w": rewards_w.tolist(),
        "rewards_l": rewards_l.tolist(),
        "accuracy": accuracy,
        "beta": beta,
    }


class DPOLoss:
    """Stateful DPO loss with running statistics."""

    def __init__(self, beta: float = 0.1):
        self.beta = beta
        self.history = []

    def __call__(self, policy_w, policy_l, ref_w, ref_l):
        """Compute DPO loss and record in history."""
        result = compute_dpo_loss(policy_w, policy_l, ref_w, ref_l, self.beta)
        self.history.append(result["loss"])
        return result

    def reset(self):
        """Clear loss history."""
        self.history.clear()
