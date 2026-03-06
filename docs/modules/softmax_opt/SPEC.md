# Softmax Optimization Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides numerically stable softmax implementations including standard softmax, log-softmax, online softmax (single-pass algorithm), and safe softmax with overflow prevention.

## Functional Requirements

1. Standard softmax with temperature scaling and max-subtraction for numerical stability
2. Log-softmax via log-sum-exp trick for numerically stable log probabilities
3. Online softmax: single-pass algorithm avoiding the need to store all logits simultaneously


## Interface

```python
from codomyrmex.softmax_opt import softmax, log_softmax, online_softmax, safe_softmax

probs = softmax(logits, temperature=0.8)
log_probs = log_softmax(logits)
online_probs = online_softmax(logits)
```

## Exports

softmax, log_softmax, online_softmax, safe_softmax

## Navigation

- [Source README](../../src/codomyrmex/softmax_opt/README.md) | [AGENTS.md](AGENTS.md)
