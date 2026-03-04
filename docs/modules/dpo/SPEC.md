# Direct Preference Optimization Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements DPO (Direct Preference Optimization) loss function for aligning language models with human preferences without explicit reward modeling. Computes the implicit reward margin between preferred and dispreferred completions.

## Functional Requirements

1. DPO loss computation from policy/reference log probability ratios on preference pairs
2. Implicit reward computation as beta * (log pi(y|x) - log ref(y|x))
3. Preference accuracy metric to track alignment with human preference labels


## Interface

```python
from codomyrmex.dpo import DPOLoss, compute_dpo_loss, compute_log_probs

result = compute_dpo_loss(policy_w, policy_l, ref_w, ref_l, beta=0.1)
print(result["loss"], result["accuracy"])
```

## Exports

DPOLoss, compute_dpo_loss, compute_log_probs

## Navigation

- [Source README](../../src/codomyrmex/dpo/README.md) | [AGENTS.md](AGENTS.md)
