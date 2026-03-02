# LoRA -- Technical Specification

## Architecture

### Weight Decomposition

LoRA decomposes a weight update into two low-rank matrices:

```
W = W_0 + B @ A * (alpha / r)
```

- W_0 in R^{d x k}: Frozen pretrained weight
- A in R^{r x k}: Initialized with Kaiming uniform (randn * sqrt(2/k))
- B in R^{d x r}: Initialized to zero
- r: Rank (r << min(d, k))
- alpha: Scaling factor
- scaling = alpha / r

### Initialization

- B = 0 ensures initial delta = 0 (training starts from pretrained behavior)
- A uses Kaiming initialization for good gradient flow

### Forward Pass

For input x in R^{batch x k}:
1. base = x @ W_0^T  (standard linear)
2. lora = x @ A^T @ B^T * scaling  (low-rank adaptation)
3. output = base + lora

### Merge/Unmerge

- Merge: W_0 <- W_0 + B @ A * scaling (absorb delta for inference)
- Unmerge: Restore original W_0 (requires passing the original weight)

## Supported Operations

| Operation | Description |
|-----------|-------------|
| `forward(x)` | Compute adapted output |
| `merge()` | Absorb LoRA delta into W_0 |
| `unmerge(original_W)` | Restore original weight |
| `get_delta()` | Return B @ A * scaling |
| `effective_rank` | Matrix rank of the delta |

## Numerical Stability

- Standard float64 NumPy operations
- No special handling needed at typical scales

## Limitations

- CPU only (NumPy, no GPU acceleration)
- No dropout implementation on the LoRA path (config field reserved)
- Not designed for large-scale training (use PEFT/HuggingFace for that)
