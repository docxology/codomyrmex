# Neural -- Agent Integration Guide

## Module Purpose

Provides from-scratch Transformer and attention primitives for AI agents that need to demonstrate, inspect, or run neural network forward passes without framework dependencies.

## MCP Tools

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `transformer_encode` | Run forward pass through a random Transformer encoder | `sequence_length`, `d_model`, `n_heads`, `n_layers` | `{status, output_shape, d_model, n_heads, n_layers, sequence_length}` |
| `attention_forward` | Run multi-head attention on random inputs | `seq_len`, `d_model`, `n_heads` | `{status, output_shape, attention_weights_shape, d_k}` |

## Agent Use Cases

### Architecture Exploration
An agent can use `transformer_encode` to verify output shapes for different hyperparameter configurations (d_model, n_heads, n_layers) before committing to a design.

### Attention Visualization
Use `attention_forward` to generate attention weight matrices that can be inspected or visualized to understand attention patterns.

### Educational Demonstration
Agents can walk through the Transformer architecture step by step, using the Python API directly to show intermediate representations at each layer.

## Example Agent Workflow

```
1. Agent receives: "Show me how a 4-head attention mechanism works on a sequence of 8 tokens"
2. Agent calls: attention_forward(seq_len=8, d_model=32, n_heads=4)
3. Response: {"status": "success", "output_shape": [1, 8, 32], "attention_weights_shape": [1, 4, 8, 8], "d_k": 8}
4. Agent explains: "Each of the 4 heads independently computes an 8x8 attention matrix..."
```

## Python API (for direct agent use)

```python
from codomyrmex.neural import (
    scaled_dot_product_attention,
    MultiHeadAttention,
    TransformerBlock,
    TransformerEncoder,
    TransformerDecoder,
    LayerNorm, FeedForward, PositionalEncoding, Embedding,
    gelu, relu, swish,
)
```
