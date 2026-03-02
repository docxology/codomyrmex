# Agent Guidelines -- Knowledge Distillation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Knowledge Distillation provides teacher-student model compression via soft label transfer.
Implements Hinton et al. (2015) with temperature-scaled softmax and combined KL/CE loss.
One MCP tool (`distillation_compute_loss`) exposes the computation to PAI agents.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `DistillationLoss`, `soft_labels`, `distillation_loss` |
| `pipeline.py` | Core implementation (soft_labels, distillation_loss, DistillationLoss) |
| `mcp_tools.py` | MCP tool: `distillation_compute_loss` |

## Key Classes

- **DistillationLoss** -- Stateful loss wrapper with temperature and alpha
- **soft_labels** -- Temperature-scaled softmax for generating soft targets
- **distillation_loss** -- Combined KL + CE loss function

## Agent Instructions

1. **Generate soft targets** -- Use `soft_labels(logits, temperature)` from teacher
2. **Compute loss** -- Use `distillation_loss(student, teacher, labels, T, alpha)`
3. **Tune temperature** -- Higher T = softer targets (more dark knowledge)
4. **Tune alpha** -- Higher alpha = more weight on distillation vs hard labels

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `distillation_compute_loss` | Compute KD loss on synthetic teacher-student data | SAFE |

## Operating Contracts

- `soft_labels` uses numerically stable softmax (max-subtraction trick)
- `distillation_loss` with `true_labels=None` sets CE loss to 0
- T^2 normalization is applied to the KL component (standard practice)
- Teacher accuracy is computed as argmax match against true_labels

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full computation | `distillation_compute_loss` | SAFE |
| **Architect** | Temperature/alpha analysis | `distillation_compute_loss` | SAFE |
| **QATester** | Verification | `distillation_compute_loss` -- loss component checks | SAFE |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
