# Interpretability Specification

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides Sparse Autoencoder (SAE) tools for mechanistic interpretability of neural networks. Trains SAEs on activation data to discover interpretable sparse features and analyze activation patterns.

## Functional Requirements

1. Sparse Autoencoder training with L1 sparsity penalty on activation data
2. Feature analysis: top activated features, sparsity metrics, and activation frequencies
3. Configurable d_input, d_features, learning rate, and L1 penalty for SAE architecture


## Interface

```python
from codomyrmex.interpretability import SparseAutoencoder, train_sae, analyze_features

sae = train_sae(activations, d_features=256, n_steps=100, lambda_l1=1e-3)
analysis = analyze_features(sae, activations)
```

## Exports

SparseAutoencoder, train_sae, analyze_features

## Navigation

- [Source README](../../src/codomyrmex/interpretability/README.md) | [AGENTS.md](AGENTS.md)
