# SSM - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `ssm` module provides a from-scratch implementation of State Space Models, specifically the Mamba selective SSM architecture. An alternative to Transformers for sequence modelling with linear-time complexity.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `MambaBlock` | Full Mamba block with selective SSM, gating, and residual connection |
| `SelectiveSSM` | Core selective state-space model with input-dependent dynamics |

### 2.2 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `mamba_forward` | `(x, ssm_params) -> ndarray` | Run a forward pass through the Mamba SSM |

## 3. Usage Example

```python
from codomyrmex.ssm import MambaBlock
import numpy as np

block = MambaBlock(d_model=256, d_state=16, d_conv=4)
x = np.random.randn(1, 128, 256)  # (batch, seq_len, d_model)
output = block(x)
print(output.shape)  # (1, 128, 256)
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
