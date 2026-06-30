# Neural - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `neural` module provides from-scratch neural network primitives including Transformer blocks, attention mechanisms, layer types, and activation functions. Pure NumPy implementations for educational and prototyping purposes.

## 2. Core Components

### 2.1 Transformer

| Class | Description |
|-------|-------------|
| `TransformerBlock` | Single transformer block (attention + feed-forward + layer norm) |
| `TransformerEncoder` | Stack of transformer encoder blocks |
| `TransformerDecoder` | Stack of transformer decoder blocks with causal masking |

### 2.2 Attention

| Class/Function | Description |
|----------------|-------------|
| `MultiHeadAttention` | Multi-head attention with Q/K/V projections |
| `scaled_dot_product_attention` | Core scaled dot-product attention function |
| `flash_attention` | Memory-efficient flash attention implementation |
| `verify_flash_vs_standard` | Verify numerical equivalence of flash vs standard attention |

### 2.3 Layers

| Class | Description |
|-------|-------------|
| `Embedding` | Token embedding lookup table |
| `PositionalEncoding` | Sinusoidal positional encoding |
| `FeedForward` | Two-layer feed-forward network with activation |
| `LayerNorm` | Layer normalisation |

### 2.4 Activations

| Function | Description |
|----------|-------------|
| `relu` | Rectified Linear Unit |
| `gelu` | Gaussian Error Linear Unit |
| `swish` | Swish/SiLU activation |

## 3. Usage Example

```python
from codomyrmex.neural import TransformerBlock, Embedding, PositionalEncoding
import numpy as np

embed = Embedding(vocab_size=50257, d_model=256)
pos = PositionalEncoding(d_model=256, max_len=512)
block = TransformerBlock(d_model=256, n_heads=8)

tokens = np.array([[1, 42, 500, 7]])
x = embed(tokens) + pos(tokens.shape[1])
output = block(x)
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
