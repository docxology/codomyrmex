# Agent Guidelines -- DPO

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

DPO (Direct Preference Optimization) provides preference-based alignment loss computation.
Implements the Rafailov et al. (2023) loss that directly optimizes a policy from human preference
data without requiring a separate reward model. One MCP tool (`dpo_compute_loss`) exposes DPO
computation to PAI agents.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `DPOLoss`, `compute_dpo_loss`, `compute_log_probs` |
| `loss.py` | DPO loss implementation and log probability computation |
| `mcp_tools.py` | MCP tool: `dpo_compute_loss` |

## Key Classes

- **DPOLoss** -- Stateful DPO loss with running history tracking
- **compute_dpo_loss** -- Core DPO loss function (functional interface)
- **compute_log_probs** -- Numerically stable log probability computation from logits

## Agent Instructions

1. **Compute log probs** -- Use `compute_log_probs(logits, labels)` to get per-token log probs
2. **Compute DPO loss** -- Use `compute_dpo_loss(policy_w, policy_l, ref_w, ref_l, beta)`
3. **Track history** -- Use `DPOLoss` class for stateful loss tracking across steps

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `dpo_compute_loss` | Compute DPO loss on synthetic preference data | SAFE |

## Operating Contracts

- `compute_log_probs` uses numerically stable log-softmax
- Tokens with `ignore_index=-100` are zeroed out in log probability computation
- `DPOLoss.history` tracks per-step scalar losses; call `reset()` to clear
- beta > 0 is required (beta=0 degenerates the loss)

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full computation | `dpo_compute_loss` | SAFE |
| **Architect** | Loss analysis | `dpo_compute_loss` -- beta sensitivity | SAFE |
| **QATester** | Verification | `dpo_compute_loss` -- accuracy checks | SAFE |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
