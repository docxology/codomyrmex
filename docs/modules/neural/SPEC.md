# Neural Network Primitives Specification

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides from-scratch Transformer implementation including multi-head attention, flash attention, feed-forward networks, layer normalization, positional encoding, and activation functions. All implemented in pure NumPy.

## Functional Requirements

1. Multi-head scaled dot-product attention with configurable d_model and n_heads
2. Flash attention with tiled computation for memory-efficient attention
3. TransformerEncoder and TransformerDecoder with stacked TransformerBlock layers
4. LayerNorm, FeedForward, PositionalEncoding, and Embedding layers
5. Activation functions: gelu, relu, swish


## Interface

```python
from codomyrmex.neural import TransformerEncoder, MultiHeadAttention, flash_attention

encoder = TransformerEncoder(n_layers=6, d_model=512, n_heads=8, d_ff=2048)
output = encoder(input_tensor)
attn_output, weights = MultiHeadAttention(512, 8)(q, k, v)
```

## Exports

MultiHeadAttention, scaled_dot_product_attention, flash_attention, verify_flash_vs_standard, TransformerBlock, TransformerEncoder, TransformerDecoder, LayerNorm, FeedForward, PositionalEncoding, Embedding, gelu, relu, swish

## Navigation

- [Source README](../../src/codomyrmex/neural/README.md) | [AGENTS.md](AGENTS.md)
