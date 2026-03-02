# DPO -- Technical Specification

## Architecture

### Loss Function

The DPO loss eliminates the need for a separate reward model:

```
Loss = -E[log sigmoid(beta * (r_w - r_l))]
```

where implicit rewards are:
```
r_w = beta * (log_pi(y_w | x) - log_ref(y_w | x))
r_l = beta * (log_pi(y_l | x) - log_ref(y_l | x))
```

### Log Probability Computation

Per-token log probs use numerically stable log-softmax:
1. Subtract max logit per position (shift for stability)
2. Compute log(sum(exp(shifted))) as the normalizer
3. log_prob = shifted_logit - normalizer
4. Gather at label positions; zero out ignore_index tokens

### Accuracy Metric

Accuracy = fraction of preference pairs where rewards_w > rewards_l.
Perfect accuracy (1.0) means the policy always prefers the human-chosen winner.

## Supported Operations

| Operation | Description |
|-----------|-------------|
| `compute_log_probs(logits, labels)` | Per-token log probs from (batch, seq, vocab) logits |
| `compute_dpo_loss(...)` | DPO loss from per-sequence log probs |
| `DPOLoss(beta)(...)` | Stateful wrapper with history |

## Numerical Stability

- Log-softmax uses max-subtraction trick to prevent overflow
- Sigmoid computed as 1/(1+exp(-x)) with epsilon 1e-9 inside log
- All operations in float64 (NumPy default)

## Limitations

- CPU only (NumPy, no GPU acceleration)
- No gradient computation (loss value only, not backward pass)
- Designed for understanding DPO mechanics, not production RLHF
