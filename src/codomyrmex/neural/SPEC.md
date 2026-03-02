# Neural -- API Specification

## Public API

### Functions

#### `scaled_dot_product_attention(Q, K, V, mask=None)`
Scaled dot-product attention: softmax(Q @ K^T / sqrt(d_k)) @ V

- **Q**: `np.ndarray` shape `(..., seq_len_q, d_k)`
- **K**: `np.ndarray` shape `(..., seq_len_k, d_k)`
- **V**: `np.ndarray` shape `(..., seq_len_k, d_v)`
- **mask**: Optional `np.ndarray` boolean, `True` = attend, `False` = mask out
- **Returns**: `(output, weights)` -- output shape `(..., seq_len_q, d_v)`, weights shape `(..., seq_len_q, seq_len_k)`

#### `gelu(x)`, `relu(x)`, `swish(x)`
Activation functions operating element-wise on `np.ndarray`.

### Classes

#### `MultiHeadAttention(d_model, n_heads, dropout=0.0)`
- **forward(query, key, value, mask=None)**: Returns `(output, weights)`
- Raises `AssertionError` if `d_model % n_heads != 0`

#### `LayerNorm(d_model, eps=1e-6)`
- **forward(x)**: Normalize across last dimension

#### `FeedForward(d_model, d_ff)`
- **forward(x)**: Two-layer MLP with GELU activation

#### `PositionalEncoding(d_model, max_len=5000)`
- **forward(x)**: Add sinusoidal positional encoding

#### `Embedding(vocab_size, d_model)`
- **forward(token_ids)**: Lookup + scale by sqrt(d_model)

#### `TransformerBlock(d_model, n_heads, d_ff, dropout=0.0)`
- **forward(x, mask=None)**: Single encoder block (pre-LN)

#### `TransformerEncoder(n_layers, d_model, n_heads, d_ff, vocab_size=0, max_len=512, dropout=0.0)`
- **forward(x, mask=None)**: Full encoder stack. Accepts token IDs (if vocab_size > 0) or float embeddings.

#### `TransformerDecoder(n_layers, d_model, n_heads, d_ff)`
- **forward(tgt, memory, tgt_mask=None, memory_mask=None)**: Decoder stack with cross-attention.

## MCP Tools

| Tool | Category | Inputs | Output |
|------|----------|--------|--------|
| `transformer_encode` | neural | `sequence_length`, `d_model`, `n_heads`, `n_layers` | `{status, output_shape, ...}` |
| `attention_forward` | neural | `seq_len`, `d_model`, `n_heads` | `{status, output_shape, attention_weights_shape, d_k}` |

## Invariants

1. All attention weight rows sum to 1.0 (softmax normalization)
2. Output shapes preserve batch and sequence dimensions
3. Numerically stable softmax (max subtraction before exp)
4. Pre-LN residual connections for training stability
5. Embedding scaling by sqrt(d_model) per Vaswani et al.
