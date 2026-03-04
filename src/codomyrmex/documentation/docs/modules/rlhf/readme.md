# RLHF Pipeline

Proximal Policy Optimization (PPO) implementation for reinforcement learning from human feedback, built from scratch with NumPy.

## Overview

The RLHF module provides a complete PPO training pipeline:

- **Actor**: Policy network outputting action log-probabilities via log-softmax
- **Critic**: Value function network estimating expected returns
- **RewardModel**: Bradley-Terry preference model for learning from human comparisons
- **GAE**: Generalized Advantage Estimation (Schulman et al. 2015)
- **PPO Step**: Clipped objective with value loss and entropy bonus

## Quick Start

```python
from codomyrmex.rlhf import PPOTrainer, RewardModel
from codomyrmex.rlhf.ppo import compute_gae
import numpy as np

# Create trainer
trainer = PPOTrainer(d_state=8, d_action=4)

# Generate synthetic rollout
states = np.random.randn(16, 8)
actions = np.random.randint(0, 4, 16)
rewards = np.random.randn(16) * 0.1

# Get baselines
log_probs_all = trainer.actor(states)
old_log_probs = np.array([log_probs_all[i, actions[i]] for i in range(16)])
values = trainer.critic(states)

# Compute advantages
advantages, returns = compute_gae(rewards, values, last_value=0.0)

# PPO step
result = trainer.compute_loss(states, actions, old_log_probs, advantages, returns)
print(result)  # policy_loss, value_loss, entropy, total_loss
```

## Dependencies

- `numpy` (core dependency)
- No external RL libraries
