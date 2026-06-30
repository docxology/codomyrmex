# Softmax Opt - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `softmax_opt` module provides numerically stable softmax implementations including the online (streaming) algorithm. Prevents overflow/underflow through log-sum-exp tricks.

## 2. Core Components

### 2.1 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `softmax` | `(x) -> ndarray` | Standard numerically stable softmax |
| `safe_softmax` | `(x) -> ndarray` | Extra-safe softmax with denormalized float handling |
| `online_softmax` | `(x) -> ndarray` | Online (streaming) softmax — single-pass algorithm |
| `log_softmax` | `(x) -> ndarray` | Log-softmax for numerical stability in loss computation |

## 3. Usage Example

```python
from codomyrmex.softmax_opt import softmax, online_softmax, log_softmax
import numpy as np

logits = np.array([2.0, 1.0, 0.1, -1.0])
probs = softmax(logits)
log_probs = log_softmax(logits)

# Online algorithm processes elements in one pass
streaming_probs = online_softmax(logits)
assert np.allclose(probs, streaming_probs)
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
