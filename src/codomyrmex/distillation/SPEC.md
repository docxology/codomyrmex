# Knowledge Distillation -- Technical Specification

## Architecture

### Soft Label Generation

Temperature-scaled softmax converts teacher logits to soft targets:

```
p(y|x, T) = exp(z_i / T) / sum(exp(z_j / T))
```

At T=1: standard softmax. At T>1: softer distribution revealing inter-class relationships ("dark knowledge").

### Loss Function

Combined loss with two components:

```
L = alpha * T^2 * KL(student_soft || teacher_soft) + (1 - alpha) * CE(student, labels)
```

- KL divergence: sum(teacher * log(teacher / student)) over classes
- CE: standard cross-entropy with hard labels (log-softmax at T=1)
- T^2: normalizes gradient magnitude when using elevated temperature

### Temperature Effects

| Temperature | Max Prob | Distribution | Use Case |
|------------|----------|-------------|----------|
| T = 1 | Peaked | Standard softmax | Normal inference |
| T = 4 | Moderate | Soft | Standard distillation |
| T = 20 | Very flat | Nearly uniform | Maximum dark knowledge |

## Supported Operations

| Operation | Description |
|-----------|-------------|
| `soft_labels(logits, T)` | Temperature-scaled softmax |
| `distillation_loss(...)` | Combined KL + CE loss |
| `DistillationLoss(T, alpha)(...)` | Stateful wrapper |

## Numerical Stability

- Softmax uses max-subtraction trick
- KL uses epsilon 1e-9 to prevent log(0)
- Cross-entropy uses log-softmax (not log of softmax)

## Limitations

- CPU only (NumPy, no GPU)
- No gradient computation (loss value only)
- 2D input only (batch, classes); no sequence dimension in loss
