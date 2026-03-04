# Interpretability Module

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `interpretability` module provides Sparse Autoencoder (SAE) implementations for mechanistic interpretability of neural networks. SAEs learn a sparse overcomplete basis for neural network activations, decomposing superposition in transformer residual streams into interpretable "features" (Elhage et al. 2022, Cunningham et al. 2023). The module includes training, feature analysis, and activation statistics. Pure Python and NumPy -- no PyTorch dependency.

## Architecture

The module is contained in `sae.py` with three components:

- **`SparseAutoencoder`** -- the core SAE with encode, decode, loss, and train_step methods
  - Encoder: ReLU(W_enc @ (x - b_dec) + b_enc) producing sparse features
  - Decoder: W_dec @ features + b_dec reconstructing activations
  - Loss: MSE reconstruction + L1 sparsity penalty
  - Decoder columns normalized to unit norm (standard practice)

- **`train_sae()`** -- convenience training function with mini-batch SGD
- **`analyze_features()`** -- feature activation statistics and correlation analysis

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `SparseAutoencoder` | `sae.py` | SAE with encode, decode, forward, loss, and train_step |
| `train_sae` | `sae.py` | Train an SAE on activation data with configurable hyperparameters |
| `analyze_features` | `sae.py` | Compute feature activation frequency, top features, correlations |

## Quick Start

```python
import numpy as np
from codomyrmex.interpretability import SparseAutoencoder, train_sae, analyze_features

# Simulate transformer activations (1000 samples, 256-dim)
activations = np.random.randn(1000, 256)

# Train a 4x overcomplete SAE
sae = train_sae(activations, d_features=1024, n_steps=100, lambda_l1=1e-3, seed=42)

# Analyze learned features
stats = analyze_features(sae, activations)
print(f"Mean active features: {stats['mean_active_features']:.1f}")
print(f"Top feature IDs: {stats['top_feature_ids']}")

# Direct usage
loss_info = sae.loss(activations[:32])
print(f"Reconstruction loss: {loss_info['reconstruction_loss']:.4f}")
print(f"Sparsity ratio: {loss_info['sparsity_ratio']:.4f}")
```

## SAE Loss Components

The `loss()` method returns a dictionary with:

- `total_loss` -- reconstruction_loss + sparsity_loss
- `reconstruction_loss` -- MSE between input and reconstruction
- `sparsity_loss` -- lambda_l1 * mean L1 norm of feature activations
- `mean_active_features` -- average number of non-zero features per sample
- `sparsity_ratio` -- fraction of features active (lower = sparser)

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| VERIFY | Analyze model internals via feature decomposition |
| LEARN | Extract interpretable features from trained model activations |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/interpretability/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports: SparseAutoencoder, train_sae, analyze_features |
| `sae.py` | Full SAE implementation with training and analysis |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [neural](../neural/) -- Transformer layers whose activations SAEs analyze
- [autograd](../autograd/) -- Gradient computation used in SAE training
- [logit_processor](../logit_processor/) -- Output-level analysis (vs SAE's internal analysis)

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/interpretability/`](../../../src/codomyrmex/interpretability/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)
