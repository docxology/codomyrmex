# Knowledge Distillation Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements teacher-student knowledge distillation training pipeline. Computes distillation loss combining soft-label KL divergence with hard-label cross-entropy for model compression.

## Functional Requirements

1. Soft-label generation from teacher logits using temperature-scaled softmax
2. Combined distillation loss: alpha * KL(student||teacher) + (1-alpha) * CE(student, labels)
3. Configurable temperature (T) and alpha weighting for loss balance


## Interface

```python
from codomyrmex.distillation import DistillationLoss, distillation_loss, soft_labels

result = distillation_loss(
    student_logits, teacher_logits, true_labels,
    temperature=4.0, alpha=0.7
)
print(result["total_loss"], result["distillation_loss"], result["ce_loss"])
```

## Exports

DistillationLoss, soft_labels, distillation_loss

## Navigation

- [Source README](../../src/codomyrmex/distillation/README.md) | [AGENTS.md](AGENTS.md)
