# SSM -- State Space Models

Pure NumPy implementation of Mamba (Gu & Dao 2023), a selective state space model that provides an alternative to Transformer attention with linear-time sequence processing.

## Overview

State Space Models (SSMs) process sequences through a continuous-time linear system discretized for digital computation. Mamba extends classical SSMs (like S4) by making the system matrices **input-dependent** (selective), allowing the model to dynamically focus on relevant parts of the input.

### Key Components

| Component | Description |
|-----------|-------------|
| `SelectiveSSM` | Core S6 kernel with input-dependent B, C, Delta matrices |
| `MambaBlock` | Full block: input projection, causal conv1d, SSM, gated output |
| `mamba_forward` | Stack N MambaBlock layers with residual connections |

### Architecture

```
Input x
  |
  v
[Linear projection] --> x_path (d_inner) + gate z (d_inner)
  |                                          |
  v                                          v
[Causal Conv1d]                           [SiLU]
  |                                          |
  v                                          |
[SiLU]                                       |
  |                                          |
  v                                          |
[SelectiveSSM]                               |
  |                                          |
  v                                          |
[Element-wise multiply] <--------------------+
  |
  v
[Output projection] --> d_model
```

## Usage

```python
import numpy as np
from codomyrmex.ssm import SelectiveSSM, MambaBlock, mamba_forward

# Single SSM layer
ssm = SelectiveSSM(d_model=64, d_state=16)
x = np.random.randn(1, 128, 64)  # (batch, seq, d_model)
y = ssm.forward(x)  # (1, 128, 64)

# Full Mamba block
block = MambaBlock(d_model=64, d_state=16, d_conv=4)
out = block(x)  # (1, 128, 64)

# Stacked Mamba model
out = mamba_forward(x, n_layers=4, d_state=16)  # (1, 128, 64)
```

## Theory

### Selective State Space (S6)

The continuous-time state equation:
```
h'(t) = A * h(t) + B(t) * x(t)
y(t)  = C(t) * h(t) + D * x(t)
```

Discretized via zero-order hold (ZOH):
```
h_t = A_bar_t * h_{t-1} + B_bar_t * x_t
y_t = C_t * h_t + D * x_t
```

where `A_bar = exp(Delta * A)` and `B_bar = Delta * B`.

The key innovation is that B, C, and Delta are **input-dependent** projections, computed from x at each timestep. This selectivity allows Mamba to match Transformer performance while maintaining O(N) complexity.

### HiPPO Initialization

Matrix A is initialized following the HiPPO framework: `A[n] = -(n+1)` on the diagonal. This initialization enables the state to approximate the Legendre polynomial basis of the input history.

## Dependencies

- NumPy (core dependency, no optional extras needed)

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/ssm/ -v
```
