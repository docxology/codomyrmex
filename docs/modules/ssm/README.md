# SSM (State Space Models) Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `ssm` module implements the Mamba selective state space model from Gu & Dao (2023). Unlike S4 which uses time-invariant parameters, Mamba makes B, C, and Delta input-dependent (selective), allowing the model to focus on or ignore different parts of the input sequence. The module provides both the low-level `SelectiveSSM` (S6 core) and the full `MambaBlock` with input projection, causal convolution, gating, and output projection. Pure Python and NumPy -- no PyTorch dependency.

## Architecture

The module is contained in `mamba.py` with two main classes:

- **`SelectiveSSM`** -- the selective state space model core (S6)
  - HiPPO-initialized A matrix (diagonal: -(1, 2, ..., N))
  - Input-dependent B, C via learned projections
  - Delta via projected softplus for positivity
  - Sequential scan over timesteps

- **`MambaBlock`** -- full Mamba block wrapping SelectiveSSM
  - Input projection to 2x d_inner (SSM path + gate path)
  - Causal 1D convolution on SSM path
  - SiLU activation on both paths
  - Gated output (element-wise multiply)
  - Output projection back to d_model

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `SelectiveSSM` | `mamba.py` | Selective SSM (S6) with input-dependent B, C, Delta |
| `MambaBlock` | `mamba.py` | Full Mamba block: projection + conv + SSM + gating |
| `mamba_forward` | `mamba.py` | Convenience function for single-call forward pass |

## Quick Start

```python
import numpy as np
from codomyrmex.ssm import MambaBlock, SelectiveSSM

# Full Mamba block
block = MambaBlock(d_model=128, d_inner=256, d_state=16, d_conv=4)
x = np.random.randn(2, 50, 128)  # (batch, seq, d_model)
output = block.forward(x)
print(f"Output shape: {output.shape}")  # (2, 50, 128)

# Low-level selective SSM
ssm = SelectiveSSM(d_model=128, d_state=16)
y = ssm.forward(x)  # Sequential scan
```

## State Space Equations

The discretized selective SSM computes:

```
h_t = A_bar_t * h_{t-1} + B_bar_t * x_t    (state update)
y_t = C_t * h_t + D * x_t                    (output with skip)

where A_bar_t = exp(Delta_t * A)              (zero-order hold)
      B_bar_t = Delta_t * B_t                 (input-dependent)
```

The selectivity mechanism (input-dependent B, C, Delta) is what distinguishes Mamba from earlier S4 models.

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| BUILD | Construct Mamba-based sequence models as transformer alternatives |
| VERIFY | Compare SSM vs attention for sequence modeling tasks |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/ssm/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports: MambaBlock, SelectiveSSM, mamba_forward |
| `mamba.py` | Full Mamba implementation (SelectiveSSM + MambaBlock) |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [neural](../neural/) -- Transformer-based alternative to SSM |
- [slm](../slm/) -- Small Language Model (transformer-based, contrast with Mamba) |
- [softmax_opt](../softmax_opt/) -- SSMs avoid softmax entirely (key advantage) |

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/ssm/`](../../../src/codomyrmex/ssm/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)
