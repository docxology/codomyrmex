# LoRA -- Low-Rank Adaptation

A pure Python + NumPy implementation of LoRA (Low-Rank Adaptation) from Hu et al. (2021) for parameter-efficient fine-tuning.

## Overview

LoRA reparameterizes a pretrained weight matrix W_0 as:

```
W = W_0 + B @ A * (alpha / r)
```

where A in R^{r x k} and B in R^{d x r}, with r << min(d, k). Only A and B are trained; W_0 is frozen.

Key insight: B is initialized to zero, so the initial LoRA output is zero (no modification at start). This ensures training begins from the pretrained model's behavior.

## Quick Start

```python
import numpy as np
from codomyrmex.lora import LoRALayer, LoRAConfig, apply_lora, merge_lora

# Wrap a pretrained weight with LoRA
W = np.random.randn(512, 256)
layer = apply_lora(W, rank=8, alpha=16.0)

# Forward pass: output = x @ W_0^T + x @ A^T @ B^T * scaling
x = np.random.randn(4, 256)
output = layer(x)  # (4, 512)

# Train A and B (gradient updates go here)
# ...

# Merge for inference (no LoRA overhead)
W_merged = merge_lora(layer)
```

## Parameter Efficiency

For W in R^{512 x 256} with rank=8:
- Full params: 512 * 256 = 131,072
- LoRA params: 8 * 256 + 512 * 8 = 6,144
- Reduction: 95.3%

## Dependencies

- `numpy` (core dependency, already in codomyrmex)
- No PyTorch or external ML library required
