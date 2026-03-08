# Neural Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `neural` module provides from-scratch implementations of core neural network primitives including the full Transformer architecture from "Attention Is All You Need" (Vaswani et al. 2017), Flash Attention (Dao et al. 2022), activation functions, and foundational layers. All implementations are pure Python and NumPy with no PyTorch dependency, serving as both educational references and functional building blocks for other codomyrmex modules.

## Architecture

The module is organized across five files:

- **`layers.py`** -- LayerNorm, FeedForward, PositionalEncoding, Embedding
- **`attention.py`** -- scaled_dot_product_attention, MultiHeadAttention
- **`flash_attention.py`** -- memory-efficient tiled attention (O(N) memory vs O(N^2))
- **`activations.py`** -- GELU, ReLU, Swish activation functions
- **`transformer.py`** -- TransformerBlock, TransformerEncoder, TransformerDecoder

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `MultiHeadAttention` | `attention.py` | Multi-head attention with Q/K/V projections |
| `scaled_dot_product_attention` | `attention.py` | Core attention: softmax(QK^T/sqrt(d_k))V |
| `flash_attention` | `flash_attention.py` | Memory-efficient tiled attention (Dao et al. 2022) |
| `verify_flash_vs_standard` | `flash_attention.py` | Correctness check: flash vs standard attention |
| `TransformerBlock` | `transformer.py` | Pre-LN transformer block (self-attn + FFN + residuals) |
| `TransformerEncoder` | `transformer.py` | Stack of N encoder blocks with optional embeddings |
| `TransformerDecoder` | `transformer.py` | Decoder with causal masking and cross-attention |
| `LayerNorm` | `layers.py` | Layer normalization (Ba et al. 2016) |
| `FeedForward` | `layers.py` | Position-wise FFN with GELU activation |
| `PositionalEncoding` | `layers.py` | Sinusoidal positional encoding (Vaswani et al. 2017) |
| `Embedding` | `layers.py` | Token embedding lookup with sqrt(d_model) scaling |
| `gelu`, `relu`, `swish` | `activations.py` | Standard activation functions |

## Quick Start

```python
import numpy as np
from codomyrmex.neural import (
    TransformerBlock, MultiHeadAttention, LayerNorm,
    Embedding, PositionalEncoding, flash_attention
)

# Build a transformer block
block = TransformerBlock(d_model=256, n_heads=8, d_ff=1024)
x = np.random.randn(2, 20, 256)  # (batch, seq, d_model)
output = block(x)  # (2, 20, 256)

# Flash Attention (O(N) memory)
Q = np.random.randn(2, 4, 64, 32)  # (batch, heads, seq, d_k)
K = np.random.randn(2, 4, 64, 32)
V = np.random.randn(2, 4, 64, 32)
out = flash_attention(Q, K, V, block_size=16, causal=True)
```

## Flash Attention

The `flash_attention` implementation uses the tiled online softmax algorithm from Dao et al. (2022). Instead of materializing the full N x N attention matrix, it processes Q/K/V in tiles, maintaining running max and normalizer statistics. This reduces memory from O(N^2) to O(N), which is critical for long sequences.

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| BUILD | Foundational primitives for custom model construction |
| VERIFY | Validate attention correctness via flash vs standard comparison |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/neural/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public re-exports of all 13 key symbols |
| `layers.py` | LayerNorm, FeedForward, PositionalEncoding, Embedding |
| `attention.py` | scaled_dot_product_attention, MultiHeadAttention |
| `flash_attention.py` | Flash Attention with tiled online softmax |
| `activations.py` | gelu, relu, swish activation functions |
| `transformer.py` | TransformerBlock, TransformerEncoder, TransformerDecoder |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [slm](../slm/) -- Small Language Model built from these neural primitives
- [autograd](../autograd/) -- Automatic differentiation for training
- [softmax_opt](../softmax_opt/) -- Optimized softmax implementations
- [matmul_kernel](../matmul_kernel/) -- Tiled matrix multiplication kernels

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/neural/`](../../../src/codomyrmex/neural/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)
