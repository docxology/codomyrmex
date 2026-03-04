# Distillation Module

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `distillation` module implements the knowledge distillation framework from Hinton et al. (2015). A student network learns from both hard labels (ground truth) and soft targets produced by a teacher network at elevated temperature. The loss combines KL divergence on soft targets with cross-entropy on hard labels, weighted by an alpha parameter. Pure Python and NumPy -- no PyTorch dependency.

## Architecture

The module is contained in a single `pipeline.py` file providing both functional and stateful APIs:

- **Functional API**: `soft_labels()` and `distillation_loss()` for one-shot computation
- **Stateful API**: `DistillationLoss` class for repeated calls with fixed temperature and alpha

The distillation loss formula is:

```
L = alpha * T^2 * KL(student_soft || teacher_soft) + (1 - alpha) * CE(student, labels)
```

The T^2 factor normalizes gradient magnitude (standard practice from Hinton et al.).

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `DistillationLoss` | `pipeline.py` | Stateful loss class with configurable temperature and alpha |
| `soft_labels` | `pipeline.py` | Convert logits to soft probability targets via temperature scaling |
| `distillation_loss` | `pipeline.py` | Compute full distillation loss with KL + CE components |

## Quick Start

```python
import numpy as np
from codomyrmex.distillation import distillation_loss, soft_labels

# Teacher and student logits (batch=4, classes=10)
teacher_logits = np.random.randn(4, 10)
student_logits = np.random.randn(4, 10)
labels = np.array([3, 7, 1, 5])

# Compute distillation loss
result = distillation_loss(
    student_logits, teacher_logits, labels,
    temperature=4.0, alpha=0.7
)
print(f"Total loss: {result['total_loss']:.4f}")
print(f"KL loss: {result['distillation_loss']:.4f}")
print(f"CE loss: {result['ce_loss']:.4f}")
print(f"Teacher accuracy: {result['teacher_accuracy']:.2%}")
```

## Loss Components

The `distillation_loss` function returns a dictionary with:

- `total_loss` -- Combined weighted loss
- `distillation_loss` -- KL divergence between soft targets (scaled by T^2)
- `ce_loss` -- Cross-entropy with hard labels
- `teacher_accuracy` -- Teacher model accuracy on ground truth
- `temperature` and `alpha` -- Configuration used

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| BUILD | Model compression via teacher-student training |
| VERIFY | Compare student vs teacher accuracy after distillation |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/distillation/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports: DistillationLoss, soft_labels, distillation_loss |
| `pipeline.py` | Full distillation implementation (soft labels, KL, CE) |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [slm](../slm/) -- Small Language Models that benefit from distillation
- [lora](../lora/) -- Parameter-efficient fine-tuning (alternative to full distillation)
- [neural](../neural/) -- Transformer primitives used in teacher/student models

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/distillation/`](../../../src/codomyrmex/distillation/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)
