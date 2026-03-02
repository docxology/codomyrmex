# Small Language Model

A tiny GPT-2 style transformer for on-device inference, built from scratch with NumPy.

## Overview

The SLM module implements a minimal decoder-only transformer:

- **Token embedding** with sinusoidal positional encoding
- **N transformer blocks** with pre-LN, causal self-attention, and feed-forward layers
- **Language model head** projecting back to vocabulary logits
- **Greedy generation** for autoregressive text completion

## Quick Start

```python
from codomyrmex.slm import SLM, SLMConfig
import numpy as np

np.random.seed(42)
config = SLMConfig(vocab_size=100, d_model=32, n_heads=2, n_layers=1)
model = SLM(config)

# Forward pass
token_ids = np.array([[1, 2, 3, 4, 5]])
logits = model.forward(token_ids)  # (1, 5, 100)

# Greedy generation
generated = model.generate([1, 2, 3], max_new_tokens=10)
print(generated)  # [1, 2, 3, ...10 new tokens...]
```

## Architecture

Uses `codomyrmex.neural` building blocks (MultiHeadAttention, FeedForward, LayerNorm) when available, with inline fallbacks for standalone use.

## Dependencies

- `numpy` (core dependency)
- `codomyrmex.neural` (optional, provides attention/layers; falls back to inline implementations)
