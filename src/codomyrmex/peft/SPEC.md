# PEFT -- Technical Specification

## Architecture

### LoRA (Low-Rank Adaptation)

- **Decomposition**: W_delta = B @ A where A: (rank, d_in), B: (d_out, rank)
- **Scaling**: output = base + (x @ A.T) @ B.T * (alpha / rank)
- **Initialization**: A ~ N(0, 2/d_in), B = 0 (zero-init ensures no perturbation at start)
- **Trainable params**: rank * (d_in + d_out)

### Prefix Tuning

- **Mechanism**: Prepend n_prefix learnable vectors to key/value sequences per layer
- **Storage**: prefix_keys and prefix_values: (n_layers, n_prefix, d_model)
- **Forward**: Concatenate prefix along sequence dimension before attention
- **Trainable params**: 2 * n_layers * n_prefix * d_model

### IA3

- **Mechanism**: Element-wise rescaling of keys (l_k), values (l_v), and FFN activations (l_ff)
- **Initialization**: All scaling vectors initialized to ones (identity at start)
- **Trainable params**: 2 * d_model + d_ff

## Parameter Comparison (d_model=512)

| Method | Params | Reduction vs Full |
|--------|--------|-------------------|
| Full fine-tune | 262,144 | 1x |
| LoRA (rank=4) | 4,096 | 64x |
| Prefix (10 tokens, 2 layers) | 20,480 | 13x |
| IA3 | 3,072 | 85x |

## Limitations

- NumPy-only (no GPU, no autograd for training)
- Demonstrates forward pass only (no backward/optimizer)
- Single-layer adapters (production LoRA applies to multiple layers)
