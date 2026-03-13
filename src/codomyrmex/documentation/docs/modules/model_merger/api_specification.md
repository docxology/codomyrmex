# Model Merger - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `model_merger` module provides model merging techniques including SLERP (Spherical Linear Interpolation), linear interpolation, and model soups for combining multiple trained models.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `ModelMerger` | Orchestrates merging of multiple model weight dictionaries |

### 2.2 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `slerp` | `(a, b, t) -> ndarray` | Spherical linear interpolation between weight tensors |
| `linear_interpolate` | `(a, b, alpha) -> ndarray` | Linear interpolation between weight tensors |
| `model_soup` | `(models, weights) -> dict` | Weighted average of multiple model weight dictionaries |

## 3. Usage Example

```python
from codomyrmex.model_merger import model_soup, slerp
import numpy as np

model_a = {"layer.weight": np.random.randn(64, 64)}
model_b = {"layer.weight": np.random.randn(64, 64)}

merged = model_soup([model_a, model_b], weights=[0.6, 0.4])
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
