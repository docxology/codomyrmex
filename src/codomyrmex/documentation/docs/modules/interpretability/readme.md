# Interpretability Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

Sparse Autoencoders (SAE) for mechanistic interpretability of neural networks.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **THINK** | Decompose neural activations into interpretable features | `sae_train`, `sae_analyze` |
| **VERIFY** | Analyze feature sparsity and reconstruction quality | `sae_analyze` |

## Key Exports

### Classes

- **`SparseAutoencoder`** -- SAE with encoder (ReLU), decoder, and L1 sparsity penalty

### Functions

- **`train_sae(activations, ...)`** -- Train an SAE on activation data
- **`analyze_features(sae, activations)`** -- Analyze learned feature patterns

## Quick Start

```python
import numpy as np
from codomyrmex.interpretability import SparseAutoencoder, train_sae, analyze_features

# Train SAE on activations
activations = np.random.randn(1000, 64)  # 1000 samples, 64-dim
sae = train_sae(activations, d_features=256, n_steps=100, seed=42)

# Analyze learned features
analysis = analyze_features(sae, activations)
print(f"Sparsity ratio: {analysis['sparsity_ratio']:.3f}")
for f in analysis["top_features"][:5]:
    print(f"  Feature {f['feature_id']}: freq={f['activation_freq']:.3f}")
```

## Directory Structure

- `sae.py` -- SparseAutoencoder class, train_sae, analyze_features
- `mcp_tools.py` -- MCP tool definitions
- `__init__.py` -- Public API re-exports

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/interpretability/ -v
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
