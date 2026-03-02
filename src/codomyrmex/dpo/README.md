# DPO -- Direct Preference Optimization

A pure Python + NumPy implementation of the DPO loss from Rafailov et al. (2023) for aligning language models with human preferences without a separate reward model.

## Overview

DPO directly optimizes a policy from preference data:

```
Loss = -log(sigmoid(beta * (log_ratio_w - log_ratio_l)))
```

where:
- log_ratio_w = log_pi(y_w | x) - log_ref(y_w | x)  (winner advantage)
- log_ratio_l = log_pi(y_l | x) - log_ref(y_l | x)  (loser advantage)
- beta controls the KL penalty (higher = more conservative)

## Quick Start

```python
import numpy as np
from codomyrmex.dpo import compute_dpo_loss, compute_log_probs, DPOLoss

# Compute DPO loss from log probabilities
policy_w = np.array([-1.0, -0.8, -1.2])  # Policy log probs on winners
policy_l = np.array([-2.0, -1.8, -2.5])  # Policy log probs on losers
ref_w = np.array([-1.1, -0.9, -1.3])     # Reference log probs
ref_l = np.array([-2.1, -1.9, -2.6])

result = compute_dpo_loss(policy_w, policy_l, ref_w, ref_l, beta=0.1)
print(f"Loss: {result['loss']:.4f}, Accuracy: {result['accuracy']:.2f}")

# Compute log probs from logits
logits = np.random.randn(2, 5, 100)  # (batch, seq, vocab)
labels = np.random.randint(0, 100, (2, 5))
log_probs = compute_log_probs(logits, labels)
```

## Dependencies

- `numpy` (core dependency, already in codomyrmex)
- No PyTorch or external ML library required
