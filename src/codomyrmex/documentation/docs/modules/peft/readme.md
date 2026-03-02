# PEFT -- Parameter-Efficient Fine-Tuning

Pure NumPy implementations of LoRA, Prefix Tuning, and IA3 adapters.

## Overview

The peft module implements three major parameter-efficient fine-tuning methods as NumPy-based adapters. These demonstrate the mathematical foundations of PEFT without requiring PyTorch or other deep learning frameworks.

## Quick Start

### LoRA (Low-Rank Adaptation)

```python
from codomyrmex.peft import LoRAAdapter
import numpy as np

adapter = LoRAAdapter(d_in=512, d_out=512, rank=4, alpha=8.0)
x = np.random.randn(2, 10, 512)  # (batch, seq, dim)
base_output = np.random.randn(2, 10, 512)
output = adapter.adapt(x, base_output=base_output)
# output = base_output + (x @ A.T) @ B.T * (alpha/rank)

print(adapter.trainable_params)  # 4096 (vs 262144 for full fine-tuning)
```

### Prefix Tuning

```python
from codomyrmex.peft import PrefixTuningAdapter
import numpy as np

adapter = PrefixTuningAdapter(d_model=256, n_prefix=10, n_layers=6)
x = np.random.randn(2, 20, 256)  # (batch, seq, dim)
output = adapter.adapt(x, layer_idx=0)
print(output.shape)  # (2, 30, 256) -- 10 prefix tokens prepended
```

### IA3

```python
from codomyrmex.peft import IA3Adapter
import numpy as np

adapter = IA3Adapter(d_model=256)
keys = np.random.randn(2, 10, 256)
scaled_keys = adapter.adapt(keys, mode="keys")
# Initially l_k = ones, so scaled_keys == keys
```

## Methods

| Method | Paper | Trainable Params | Mechanism |
|--------|-------|-----------------|-----------|
| LoRA | Hu et al. 2021 | rank * (d_in + d_out) | Low-rank weight delta |
| Prefix Tuning | Li & Liang 2021 | 2 * n_layers * n_prefix * d_model | Virtual token prepending |
| IA3 | Liu et al. 2022 | 2 * d_model + d_ff | Element-wise rescaling |

## Dependencies

- `numpy` (core dependency)
