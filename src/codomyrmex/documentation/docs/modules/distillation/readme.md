# Knowledge Distillation

A pure Python + NumPy implementation of knowledge distillation from Hinton et al. (2015) for teacher-student model compression.

## Overview

Knowledge distillation transfers "dark knowledge" from a large teacher model to a smaller student:

```
L = alpha * T^2 * KL(student_soft || teacher_soft) + (1 - alpha) * CE(student, labels)
```

where:
- T: Temperature (higher = softer probability distribution)
- alpha: Weight for distillation vs hard-label loss
- T^2: Gradient magnitude normalization factor

## Quick Start

```python
import numpy as np
from codomyrmex.distillation import soft_labels, distillation_loss, DistillationLoss

# Generate soft labels from teacher logits
teacher_logits = np.random.randn(4, 10) * 3.0
soft_targets = soft_labels(teacher_logits, temperature=4.0)

# Compute distillation loss
student_logits = np.random.randn(4, 10)
true_labels = np.argmax(teacher_logits, axis=-1)

result = distillation_loss(student_logits, teacher_logits, true_labels,
                            temperature=4.0, alpha=0.7)
print(f"Total: {result['total_loss']:.4f}")
print(f"KL: {result['distillation_loss']:.4f}")
print(f"CE: {result['ce_loss']:.4f}")

# Stateful wrapper
loss_fn = DistillationLoss(temperature=4.0, alpha=0.7)
result = loss_fn(student_logits, teacher_logits, true_labels)
```

## Dependencies

- `numpy` (core dependency, already in codomyrmex)
- No PyTorch or external ML library required
