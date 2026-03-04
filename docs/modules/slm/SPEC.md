# Small Language Model Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements a tiny GPT-2 style transformer for on-device inference. Provides configurable model architecture with token generation and forward pass capabilities in pure NumPy.

## Functional Requirements

1. GPT-2 style causal transformer architecture with configurable SLMConfig
2. Autoregressive token generation with causal masking
3. Forward pass returning logits for all vocabulary tokens at each position


## Interface

```python
from codomyrmex.slm import SLM, SLMConfig, causal_mask

config = SLMConfig(vocab_size=1000, d_model=64, n_heads=4, n_layers=2, d_ff=256, max_seq_len=128)
model = SLM(config)
logits = model.forward(token_ids)
sequence = model.generate([1, 2, 3], max_new_tokens=10)
```

## Exports

SLMConfig, SLM, causal_mask

## Navigation

- [Source README](../../src/codomyrmex/slm/README.md) | [AGENTS.md](AGENTS.md)
