# Distillation - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `distillation` module implements a knowledge distillation pipeline for compressing large teacher models into smaller student models. Provides soft-label generation and distillation loss computation.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `DistillationLoss` | Combined loss (hard label + soft label) for student training |

### 2.2 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `distillation_loss` | `(student_logits, teacher_logits, labels, temperature, alpha) -> float` | Compute the weighted distillation loss |
| `soft_labels` | `(logits, temperature) -> ndarray` | Generate soft probability targets from teacher logits |

## 3. Usage Example

```python
from codomyrmex.distillation import distillation_loss, soft_labels
import numpy as np

teacher_logits = np.array([2.0, 1.0, 0.1])
student_logits = np.array([1.5, 1.2, 0.3])
labels = np.array([1, 0, 0])

loss = distillation_loss(student_logits, teacher_logits, labels, temperature=3.0, alpha=0.7)
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
