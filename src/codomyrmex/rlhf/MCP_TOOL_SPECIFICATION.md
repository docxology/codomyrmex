# RLHF -- MCP Tool Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `rlhf` (Reinforcement Learning from Human Feedback) module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `rlhf` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `rlhf_ppo_step`

**Description**: Run a single PPO step on synthetic data and return loss metrics.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `d_state` | `int` | No | `8` | State dimension |
| `d_action` | `int` | No | `4` | Number of discrete actions |
| `batch_size` | `int` | No | `16` | Number of transitions in the batch |
| `seed` | `int` | No | `42` | Random seed for reproducibility |

**Returns**: `dict` -- Dictionary with policy_loss, value_loss, entropy, total_loss, mean_ratio, clip_fraction, and status.

**Example**:
```python
from codomyrmex.rlhf.mcp_tools import rlhf_ppo_step

result = rlhf_ppo_step(d_state=16, d_action=8, batch_size=32, seed=123)
```

---

### `rlhf_reward_score`

**Description**: Score synthetic states using the RLHF reward model.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `d_state` | `int` | No | `8` | State/response embedding dimension |
| `batch_size` | `int` | No | `4` | Number of samples to score |
| `seed` | `int` | No | `42` | Random seed for reproducibility |

**Returns**: `dict` -- Dictionary with scores (list), preference_loss, mean_score, and status.

**Example**:
```python
from codomyrmex.rlhf.mcp_tools import rlhf_reward_score

result = rlhf_reward_score(d_state=16, batch_size=8)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- no destructive operations
- **PAI Phases**: BUILD (reward modeling, PPO training), VERIFY (loss metric validation)
- **Dependencies**: Requires `numpy` and internal `ppo` module (PPOTrainer, RewardModel, compute_gae)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
