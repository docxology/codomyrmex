"""PPO (Proximal Policy Optimization) for RLHF fine-tuning.

Implements the PPO-Clip algorithm (Schulman et al. 2017) with:
- Actor-Critic architecture (separate policy and value networks)
- Generalized Advantage Estimation (Schulman et al. 2015)
- Bradley-Terry reward model for preference learning
"""
from dataclasses import dataclass

import numpy as np


@dataclass
class PPOConfig:
    """Configuration for PPO training."""

    clip_epsilon: float = 0.2  # PPO clip ratio
    value_loss_coef: float = 0.5  # VF coefficient
    entropy_coef: float = 0.01  # Entropy bonus
    max_grad_norm: float = 0.5  # Gradient clipping
    gamma: float = 0.99  # Discount factor
    gae_lambda: float = 0.95  # GAE lambda


class Actor:
    """Policy network (outputs action log-probabilities)."""

    def __init__(self, d_state: int, d_action: int):
        scale = np.sqrt(2.0 / d_state)
        self.W1 = np.random.randn(d_state, 64) * scale
        self.b1 = np.zeros(64)
        self.W2 = np.random.randn(64, d_action) * (scale * 0.1)
        self.b2 = np.zeros(d_action)

    def forward(self, state: np.ndarray) -> np.ndarray:
        """Returns log-probabilities over actions."""
        h = np.maximum(0, state @ self.W1 + self.b1)
        logits = h @ self.W2 + self.b2
        # Log-softmax
        logits_max = np.max(logits, axis=-1, keepdims=True)
        log_probs = logits - logits_max - np.log(
            np.sum(np.exp(logits - logits_max), axis=-1, keepdims=True) + 1e-9
        )
        return log_probs

    def __call__(self, x):
        """Make Actor callable."""
        return self.forward(x)


class Critic:
    """Value function network (estimates expected return)."""

    def __init__(self, d_state: int):
        scale = np.sqrt(2.0 / d_state)
        self.W1 = np.random.randn(d_state, 64) * scale
        self.b1 = np.zeros(64)
        self.W2 = np.random.randn(64, 1) * scale
        self.b2 = np.zeros(1)

    def forward(self, state: np.ndarray) -> np.ndarray:
        """Returns value estimate."""
        h = np.maximum(0, state @ self.W1 + self.b1)
        return (h @ self.W2 + self.b2).squeeze(-1)

    def __call__(self, x):
        """Make Critic callable."""
        return self.forward(x)


class RewardModel:
    """Simple reward model for RLHF (preference-based reward).

    Uses Bradley-Terry model: P(w > l) = sigmoid(r_w - r_l)
    """

    def __init__(self, d_state: int):
        scale = np.sqrt(2.0 / d_state)
        self.W1 = np.random.randn(d_state, 32) * scale
        self.b1 = np.zeros(32)
        self.W2 = np.random.randn(32, 1) * scale
        self.b2 = np.zeros(1)

    def score(self, state: np.ndarray) -> np.ndarray:
        """Return reward score for a state/response."""
        h = np.maximum(0, state @ self.W1 + self.b1)
        return (h @ self.W2 + self.b2).squeeze(-1)

    def preference_loss(self, w_states: np.ndarray, l_states: np.ndarray) -> float:
        """Bradley-Terry preference loss: -log sigmoid(r_w - r_l)."""
        r_w = self.score(w_states)
        r_l = self.score(l_states)
        return float(-np.mean(np.log(1.0 / (1.0 + np.exp(-(r_w - r_l))) + 1e-9)))


def compute_gae(
    rewards: np.ndarray,
    values: np.ndarray,
    last_value: float,
    gamma: float = 0.99,
    gae_lambda: float = 0.95,
) -> tuple[np.ndarray, np.ndarray]:
    """Generalized Advantage Estimation (Schulman et al. 2015).

    delta_t = r_t + gamma * V(s_{t+1}) - V(s_t)
    A_t = delta_t + (gamma * lambda) * A_{t+1}

    Args:
        rewards: Per-step rewards, shape (T,)
        values: Value estimates, shape (T,)
        last_value: Bootstrap value for terminal state
        gamma: Discount factor
        gae_lambda: GAE lambda for bias-variance tradeoff

    Returns:
        advantages: GAE estimates, shape (T,)
        returns: Value function targets, shape (T,)
    """
    T = len(rewards)
    advantages = np.zeros(T)
    last_adv = 0.0

    for t in reversed(range(T)):
        next_val = last_value if t == T - 1 else values[t + 1]
        delta = rewards[t] + gamma * next_val - values[t]
        last_adv = delta + gamma * gae_lambda * last_adv
        advantages[t] = last_adv

    returns = advantages + values
    return advantages, returns


def ppo_step(
    states: np.ndarray,
    actions: np.ndarray,
    old_log_probs: np.ndarray,
    advantages: np.ndarray,
    returns: np.ndarray,
    actor: Actor,
    critic: Critic,
    config: PPOConfig = None,
) -> dict:
    """Compute PPO loss components (no gradient update in NumPy version).

    PPO Clip Loss:
    L = -E[min(r_t * A_t, clip(r_t, 1-eps, 1+eps) * A_t)]
    where r_t = pi_new(a|s) / pi_old(a|s) = exp(log_pi_new - log_pi_old)

    Args:
        states: Observation states, shape (batch, d_state)
        actions: Chosen actions, shape (batch,) integer indices
        old_log_probs: Log probs under old policy, shape (batch,)
        advantages: GAE advantages, shape (batch,)
        returns: Value targets, shape (batch,)
        actor: Policy network
        critic: Value network
        config: PPO hyperparameters

    Returns:
        dict with: policy_loss, value_loss, entropy, total_loss,
                   mean_ratio, clip_fraction
    """
    if config is None:
        config = PPOConfig()

    # New log probs from current policy
    new_log_probs_all = actor(states)  # (batch, n_actions)
    batch_size = len(actions)
    new_log_probs = np.array(
        [new_log_probs_all[i, actions[i]] for i in range(batch_size)]
    )

    # Policy ratio
    ratio = np.exp(new_log_probs - old_log_probs)

    # Normalize advantages
    adv_norm = (advantages - np.mean(advantages)) / (np.std(advantages) + 1e-8)

    # Clipped objective
    unclipped = ratio * adv_norm
    clipped = (
        np.clip(ratio, 1 - config.clip_epsilon, 1 + config.clip_epsilon) * adv_norm
    )
    policy_loss = float(-np.mean(np.minimum(unclipped, clipped)))

    # Value function loss
    predicted_values = critic(states)
    value_loss = float(np.mean((predicted_values - returns) ** 2))

    # Entropy bonus
    probs = np.exp(new_log_probs_all)
    entropy = float(-np.mean(np.sum(probs * new_log_probs_all, axis=-1)))

    total_loss = (
        policy_loss + config.value_loss_coef * value_loss - config.entropy_coef * entropy
    )

    return {
        "policy_loss": policy_loss,
        "value_loss": value_loss,
        "entropy": entropy,
        "total_loss": total_loss,
        "mean_ratio": float(np.mean(ratio)),
        "clip_fraction": float(
            np.mean(ratio < (1 - config.clip_epsilon))
            + np.mean(ratio > (1 + config.clip_epsilon))
        ),
    }


class PPOTrainer:
    """Orchestrates PPO training loop."""

    def __init__(self, d_state: int, d_action: int, config: PPOConfig = None):
        self.actor = Actor(d_state, d_action)
        self.critic = Critic(d_state)
        self.config = config or PPOConfig()
        self.losses: list[float] = []

    def compute_loss(
        self, states, actions, old_log_probs, advantages, returns
    ) -> dict:
        """Compute PPO loss for one batch and record history."""
        result = ppo_step(
            states,
            actions,
            old_log_probs,
            advantages,
            returns,
            self.actor,
            self.critic,
            self.config,
        )
        self.losses.append(result["total_loss"])
        return result
