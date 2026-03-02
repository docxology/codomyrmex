# Neural Network Primitives

A from-scratch Transformer implementation using only NumPy, following "Attention Is All You Need" (Vaswani et al. 2017).

## Overview

The neural module provides core Transformer building blocks without any deep learning framework dependencies:

- **Attention**: Scaled dot-product attention and multi-head attention
- **Transformer**: Encoder and decoder blocks with pre-LN residual connections
- **Layers**: LayerNorm, FeedForward (position-wise), PositionalEncoding (sinusoidal), Embedding
- **Activations**: GELU, ReLU, Swish

All implementations operate on NumPy arrays and are suitable for educational use, prototyping, and small-scale inference.

## Quick Start

### Scaled Dot-Product Attention

```python
import numpy as np
from codomyrmex.neural import scaled_dot_product_attention

Q = np.random.randn(1, 8, 64)  # (batch, seq_q, d_k)
K = np.random.randn(1, 8, 64)  # (batch, seq_k, d_k)
V = np.random.randn(1, 8, 64)  # (batch, seq_k, d_v)

output, weights = scaled_dot_product_attention(Q, K, V)
# output: (1, 8, 64), weights: (1, 8, 8)
```

### Multi-Head Attention

```python
from codomyrmex.neural import MultiHeadAttention

mha = MultiHeadAttention(d_model=64, n_heads=4)
x = np.random.randn(2, 10, 64)  # (batch, seq, d_model)
output, attn_weights = mha(x, x, x)
# output: (2, 10, 64), attn_weights: (2, 4, 10, 10)
```

### Transformer Encoder

```python
from codomyrmex.neural import TransformerEncoder

encoder = TransformerEncoder(
    n_layers=6, d_model=64, n_heads=4, d_ff=256, vocab_size=1000
)
token_ids = np.random.randint(0, 1000, (2, 20))  # (batch, seq)
encoded = encoder(token_ids)  # (2, 20, 64)
```

### Transformer Decoder

```python
from codomyrmex.neural import TransformerDecoder

decoder = TransformerDecoder(n_layers=6, d_model=64, n_heads=4, d_ff=256)
tgt = np.random.randn(2, 15, 64)
memory = np.random.randn(2, 20, 64)  # encoder output
decoded = decoder(tgt, memory)  # (2, 15, 64)
```

## Architecture

### Pre-LN Transformer Block

Each encoder block applies:
1. LayerNorm -> Multi-Head Self-Attention -> Residual Add
2. LayerNorm -> Feed-Forward Network -> Residual Add

The pre-LN variant (applying LayerNorm before attention/FFN rather than after) provides more stable gradients during training.

### Decoder Additions

Each decoder block adds cross-attention between self-attention and FFN:
1. LayerNorm -> Masked Self-Attention -> Residual
2. LayerNorm -> Cross-Attention (to encoder memory) -> Residual
3. LayerNorm -> FFN -> Residual

## Dependencies

- `numpy` (only external dependency)
- `codomyrmex.model_context_protocol` (for MCP tool registration)

## Tests

```bash
uv run pytest src/codomyrmex/tests/unit/neural/ -v
```
