# RLHF -- PAI Integration

## Phase Mapping

| PAI Phase | Tool | Usage |
|-----------|------|-------|
| OBSERVE | `rlhf_reward_score` | Evaluate current reward model quality |
| THINK | `rlhf_ppo_step` | Analyze PPO loss components for training decisions |
| BUILD | `PPOTrainer`, `RewardModel` (Python API) | Build RL training pipelines |
| VERIFY | `rlhf_ppo_step` | Validate PPO metrics are in expected ranges |
| LEARN | `rlhf_reward_score` | Track reward model improvement over iterations |

## MCP Tools

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `rlhf_ppo_step` | rlhf | Run PPO step and return loss metrics |
| `rlhf_reward_score` | rlhf | Score states using reward model |

## Agent Providers

This module does not provide agent types. It provides computational tools that agents consume.

## Dependencies

- Foundation: `model_context_protocol` (for `@mcp_tool` decorator)
- External: `numpy`
