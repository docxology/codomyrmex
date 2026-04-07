# RLHF Pipeline Specification

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements Proximal Policy Optimization (PPO) for Reinforcement Learning from Human Feedback. Includes Actor-Critic networks, reward model with preference learning, and GAE advantage estimation for language model alignment.

## Functional Requirements

1. PPO training step with clipped surrogate objective and value function loss
2. Actor-Critic architecture with separate policy and value networks
3. RewardModel with preference loss for learning from pairwise comparisons
4. Generalized Advantage Estimation (GAE) for variance-reduced advantage computation


## Interface

```python
from codomyrmex.rlhf import PPOTrainer, Actor, Critic, RewardModel, ppo_step

trainer = PPOTrainer(d_state=8, d_action=4)
result = trainer.compute_loss(states, actions, old_log_probs, advantages, returns)
reward = RewardModel(d_state=8)
scores = reward.score(states)
```

## Exports

PPOTrainer, Actor, Critic, RewardModel, ppo_step

## Navigation

- [Source README](../../../src/codomyrmex/rlhf/README.md) | [AGENTS.md](AGENTS.md)
