# State Space Models Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements Mamba selective State Space Model (SSM) from scratch. Provides MambaBlock with selective scan mechanism for efficient sequence modeling as an alternative to attention-based transformers.

## Functional Requirements

1. Selective SSM with input-dependent state transition matrices (Mamba architecture)
2. MambaBlock combining selective scan with gated MLP projections
3. Stackable blocks via mamba_forward for multi-layer SSM models


## Interface

```python
from codomyrmex.ssm import MambaBlock, SelectiveSSM, mamba_forward

output = mamba_forward(input_tensor, n_layers=4, d_model=256, d_state=16)
block = MambaBlock(d_model=256, d_state=16)
```

## Exports

MambaBlock, SelectiveSSM, mamba_forward

## Navigation

- [Source README](../../src/codomyrmex/ssm/README.md) | [AGENTS.md](AGENTS.md)
