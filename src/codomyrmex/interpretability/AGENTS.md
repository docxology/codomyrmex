# Agent Guidelines - Interpretability

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Sparse Autoencoders (SAE) for mechanistic interpretability -- decompose neural network activations into sparse, interpretable features.

## Key Classes and Functions

- **SparseAutoencoder** -- Overcomplete autoencoder with ReLU sparsity and L1 penalty
- **train_sae** -- Train an SAE on activation data with mini-batch gradient descent
- **analyze_features** -- Compute activation frequency, sparsity ratio, and top features

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `sae_train` | Train a Sparse Autoencoder on activation data | Safe |
| `sae_analyze` | Analyze feature activation patterns of an SAE | Safe |

## Agent Instructions

1. **Overcomplete by 4x** -- Default d_features = 4 * d_input discovers more features
2. **Tune lambda_l1** -- Higher L1 penalty = sparser features but worse reconstruction
3. **Check sparsity** -- Good SAEs have sparsity_ratio < 0.1 (most features inactive)
4. **Top features** -- Use analyze_features to find the most frequently active features

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `sae_train`, `sae_analyze` | TRUSTED |
| **Researcher** | Full | Both tools -- interpretability research | SAFE |
| **Architect** | Read | `sae_analyze` -- architecture understanding | OBSERVED |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
