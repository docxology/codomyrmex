# SLM -- Technical Specification

## Architecture

### GPT-2 Decoder-Only Transformer

```
Input token IDs -> Embedding * sqrt(d_model) + Positional Encoding
    -> N x [Pre-LN -> MultiHeadAttention -> Residual -> Pre-LN -> FFN -> Residual]
    -> Final LayerNorm -> LM Head (d_model x vocab_size)
    -> Logits (batch, seq, vocab_size)
```

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| vocab_size | 1000 | Number of tokens |
| d_model | 64 | Embedding dimension |
| n_heads | 4 | Attention heads |
| n_layers | 2 | Transformer blocks |
| d_ff | 256 | Feed-forward dimension |
| max_seq_len | 128 | Maximum sequence length |

### Causal Masking

Lower-triangular boolean mask prevents attending to future tokens:
- `mask[i][j] = True` if `j <= i` (can attend)
- `mask[i][j] = False` if `j > i` (masked out)

### Generation

Greedy decoding: at each step, take argmax of logits at the last position.
Context window slides to `max_seq_len` if sequence grows longer.

## Fallback Implementations

When `codomyrmex.neural` is not importable, inline fallback classes provide:
- `_InlineLayerNorm`: Standard layer normalization
- `_InlineFeedForward`: Two-layer MLP with ReLU (instead of GELU)
- `_InlineMultiHeadAttention`: Multi-head scaled dot-product attention

## Limitations

- Random weights: produces random-looking text without training
- NumPy-only: no GPU acceleration
- Greedy decoding only (no beam search or sampling)
