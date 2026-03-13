# Interpretability - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `interpretability` module provides Sparse Autoencoders (SAE) for neural network analysis. Enables feature extraction and interpretability analysis of learned representations.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `SparseAutoencoder` | Sparse autoencoder model with L1 sparsity penalty for feature extraction |

### 2.2 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `train_sae` | `(data, hidden_dim, sparsity_weight, ...) -> SparseAutoencoder` | Train a sparse autoencoder on activation data |
| `analyze_features` | `(sae, data) -> dict` | Analyze learned features: activation patterns, sparsity, top-k features |

## 3. Usage Example

```python
from codomyrmex.interpretability import train_sae, analyze_features
import numpy as np

activations = np.random.randn(1000, 256)  # 1000 samples, 256-dim activations
sae = train_sae(activations, hidden_dim=512, sparsity_weight=0.01)

analysis = analyze_features(sae, activations)
print(f"Active features: {analysis['num_active_features']}")
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
