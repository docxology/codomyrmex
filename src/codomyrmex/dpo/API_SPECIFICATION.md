# DPO - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `dpo` module implements Direct Preference Optimization, a simpler alternative to RLHF for aligning language models with human preferences. Operates directly on preference pairs without requiring a separate reward model.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `DPOLoss` | Computes DPO loss from chosen/rejected response pairs |

### 2.2 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_dpo_loss` | `(policy_chosen, policy_rejected, ref_chosen, ref_rejected, beta) -> float` | Compute the DPO loss for a preference pair |
| `compute_log_probs` | `(logits, labels) -> ndarray` | Compute per-token log probabilities from logits |

## 3. Usage Example

```python
from codomyrmex.dpo import compute_dpo_loss, compute_log_probs
import numpy as np

policy_chosen = np.array([-1.2, -0.5])
policy_rejected = np.array([-2.0, -1.8])
ref_chosen = np.array([-1.5, -0.8])
ref_rejected = np.array([-1.9, -1.6])

loss = compute_dpo_loss(policy_chosen, policy_rejected, ref_chosen, ref_rejected, beta=0.1)
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
