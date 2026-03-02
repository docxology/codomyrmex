# RLHF -- Agent Integration Guide

## Module Purpose

Provides PPO-based RLHF training primitives for AI agents that need to fine-tune policies from human preference data or reward signals.

## MCP Tools

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `rlhf_ppo_step` | Run a PPO step on synthetic data | `d_state, d_action, batch_size, seed` | `{policy_loss, value_loss, entropy, total_loss, mean_ratio, clip_fraction}` |
| `rlhf_reward_score` | Score states using the reward model | `d_state, batch_size, seed` | `{scores, preference_loss, mean_score}` |

## Agent Use Cases

### Policy Evaluation
An agent can use `rlhf_ppo_step` to verify that PPO loss computation produces valid metrics on synthetic data.

### Reward Scoring
Use `rlhf_reward_score` to evaluate response quality via the learned reward model.

### Training Loop Monitoring
Track `clip_fraction` and `entropy` across steps to diagnose training stability.

## Example Agent Workflow

```
1. Agent receives: "Evaluate PPO training stability"
2. Agent calls: rlhf_ppo_step(d_state=8, d_action=4, batch_size=32)
3. Response: {"clip_fraction": 0.12, "entropy": 1.38, ...}
4. Agent interprets: clip_fraction < 0.3 indicates stable training
```
