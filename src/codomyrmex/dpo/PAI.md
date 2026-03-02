# Personal AI Infrastructure -- DPO Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

DPO provides Direct Preference Optimization loss computation for PAI agents. It implements the Rafailov et al. (2023) technique using pure Python + NumPy, enabling agents to understand and evaluate preference-based alignment without requiring PyTorch.

## PAI Algorithm Phase Mapping

| Phase | Activity | Key Functions/Tools |
|-------|----------|-------------------|
| **OBSERVE** | Collect preference pairs (winner/loser log probs) | `compute_log_probs` |
| **THINK** | Analyze reward margins and preference accuracy | `compute_dpo_loss` results |
| **PLAN** | Configure beta and training hyperparameters | `DPOLoss(beta=...)` |
| **BUILD** | Set up DPO loss computation pipeline | `DPOLoss`, `compute_log_probs` |
| **EXECUTE** | Compute DPO loss on preference batches | `compute_dpo_loss`, `DPOLoss.__call__` |
| **VERIFY** | Validate accuracy and loss convergence | `result["accuracy"]`, `DPOLoss.history` |
| **LEARN** | Record preference alignment metrics | `dpo_compute_loss` MCP tool |

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `dpo_compute_loss` | Compute DPO loss on synthetic preference data | SAFE |

## Agent Capabilities

| Agent Type | Primary Use | Key Functions |
|-----------|-------------|--------------|
| **Engineer** | Compute and analyze DPO loss | `compute_dpo_loss`, `DPOLoss` |
| **Architect** | Evaluate beta sensitivity, preference margins | `dpo_compute_loss` |
| **QATester** | Verify accuracy and loss formula correctness | `compute_dpo_loss`, numerical checks |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
