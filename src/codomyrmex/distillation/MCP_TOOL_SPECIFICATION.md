# Distillation — MCP Tool Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `distillation` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

The distillation module provides knowledge distillation loss computation,
useful for training student models to match teacher model outputs.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `distillation` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `distillation_compute_loss`

**Description**: Compute knowledge distillation loss on synthetic teacher-student data.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `num_classes` | `int` | No | `10` | Number of output classes |
| `batch_size` | `int` | No | `4` | Number of samples |
| `temperature` | `float` | No | `4.0` | Distillation temperature T (higher = softer probability distributions) |
| `alpha` | `float` | No | `0.7` | Weight for distillation loss vs hard-label cross-entropy loss |
| `seed` | `int` | No | `42` | Random seed for reproducibility |

**Returns**: `dict` — Dictionary with `status`, `total_loss`, `distillation_loss`, `ce_loss`, and `teacher_accuracy`.

**Example**:
```python
from codomyrmex.distillation.mcp_tools import distillation_compute_loss

result = distillation_compute_loss(
    num_classes=5, batch_size=8, temperature=2.0, alpha=0.5, seed=42
)
```

**Notes**: Generates synthetic teacher and student logits internally. The teacher produces confident logits (scaled by 3.0) and the student adds Gaussian noise. True labels are derived from teacher argmax. The `alpha` parameter controls the blend: `alpha * distillation_loss + (1-alpha) * ce_loss`.

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe — no trust check required
- **PAI Phases**: BUILD (loss function experimentation), VERIFY (distillation parameter tuning)
- **Dependencies**: `numpy`, `distillation.pipeline.distillation_loss`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
