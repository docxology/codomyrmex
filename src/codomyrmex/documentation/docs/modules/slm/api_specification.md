# SLM - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `slm` module provides a tiny GPT-2 style transformer implementation for on-device inference. A minimal but complete small language model for research and prototyping.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `SLM` | Small Language Model with transformer decoder stack |
| `SLMConfig` | Configuration dataclass (vocab_size, d_model, n_heads, n_layers, max_len) |

### 2.2 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `causal_mask` | `(seq_len) -> ndarray` | Generate a causal (lower-triangular) attention mask |

## 3. Usage Example

```python
from codomyrmex.slm import SLM, SLMConfig

config = SLMConfig(vocab_size=50257, d_model=128, n_heads=4, n_layers=4, max_len=256)
model = SLM(config)

tokens = [1, 42, 500]
logits = model.forward(tokens)
next_token = logits[-1].argmax()
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
