# Softmax Opt Module -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Algorithms

### Standard Softmax (max-subtraction)

```
softmax(x)_i = exp(x_i - max(x)) / sum_j(exp(x_j - max(x)))
```

Two passes: (1) find max, (2) compute exp and sum. The max subtraction ensures the largest exponent is exp(0) = 1, preventing overflow.

### Log-Softmax (log-sum-exp trick)

```
log_softmax(x)_i = x_i - max(x) - log(sum_j(exp(x_j - max(x))))
```

Computes log probabilities directly without intermediate softmax. More numerically stable than `log(softmax(x))` because it avoids taking log of very small numbers.

### Online Softmax (single-pass)

```
m = -inf, d = 0
for each x_i:
    m_new = max(m, x_i)
    d = d * exp(m - m_new) + exp(x_i - m_new)
    m = m_new
result_i = exp(x_i - m) / d
```

Single pass to compute running max and normalizer simultaneously. This is the key algorithm enabling Flash Attention: softmax can be computed in tiles without materializing the full attention matrix.

### Safe Softmax (epsilon-guarded)

```
safe_softmax(x)_i = exp(x_i - max(x)) / (sum_j(exp(x_j - max(x))) + eps)
```

Adds epsilon to denominator. Prevents NaN when attention masks zero out all elements in a row.

## Numerical Properties

| Variant | Overflow-safe | Underflow-safe | Passes | Use Case |
|---------|:---:|:---:|:---:|----------|
| standard | Yes | Yes | 2 | General purpose |
| log_softmax | Yes | Yes | 2 | Cross-entropy loss, KL divergence |
| online | Yes | Yes | 1* | Flash Attention, streaming |
| safe | Yes | Yes | 2 | Masked attention |

*Online requires a final pass to compute exp(x - m) / d, but max and sum are single-pass.

### Temperature Scaling

Temperature T controls distribution sharpness:
- T -> 0: argmax (one-hot)
- T = 1: standard softmax
- T -> inf: uniform distribution

Implemented as `softmax(x / T)`.

## MCP Tool Specification

### compute_softmax

```json
{
  "name": "compute_softmax",
  "category": "softmax_opt",
  "parameters": {
    "logits": {"type": "list[float]", "description": "Raw unnormalized scores"},
    "temperature": {"type": "float", "default": 1.0, "description": "Temperature scaling"},
    "variant": {"type": "string", "enum": ["standard", "log", "online"], "default": "standard"}
  },
  "returns": {
    "status": "success",
    "probabilities": "list[float]",
    "log_probs": "list[float]",
    "entropy": "float",
    "max_prob": "float",
    "sum_check": "float"
  }
}
```
