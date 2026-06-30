# RLHF - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `rlhf` module implements a Reinforcement Learning from Human Feedback pipeline with Proximal Policy Optimization (PPO) for language model alignment.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `PPOTrainer` | Orchestrates the PPO training loop (rollout, advantage estimation, policy update) |
| `Actor` | Policy network (language model) being trained |
| `Critic` | Value network estimating expected reward |
| `RewardModel` | Learned reward model from human preference data |

### 2.2 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `ppo_step` | `(actor, critic, reward_model, batch, ...) -> dict` | Execute one PPO training step and return metrics |

## 3. Usage Example

```python
from codomyrmex.rlhf import PPOTrainer, Actor, Critic, RewardModel

actor = Actor(vocab_size=50257, d_model=256)
critic = Critic(d_model=256)
reward_model = RewardModel(d_model=256)

trainer = PPOTrainer(actor, critic, reward_model, lr=1e-5)
metrics = trainer.train_step(batch)
print(f"PPO loss: {metrics['policy_loss']:.4f}")
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
