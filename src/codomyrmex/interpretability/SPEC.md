# Interpretability - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provide Sparse Autoencoder (SAE) tools for mechanistic interpretability of neural networks, enabling decomposition of superposed representations into interpretable features.

## Functional Requirements

- Sparse overcomplete autoencoder (d_features > d_input)
- ReLU activation for natural sparsity
- L1 penalty on feature activations for explicit sparsity control
- Unit-norm decoder columns (standard SAE practice)
- Feature analysis: activation frequency, sparsity ratio, top features

## Architecture

```
Encoder: x -> ReLU(W_enc @ (x - b_dec) + b_enc)  -> sparse features
Decoder: features -> W_dec @ features + b_dec      -> reconstruction
```

## Loss Function

```
L = MSE(x, x_hat) + lambda_l1 * mean(sum(|features|))
```

## Core Components

| Component | Description |
|-----------|-------------|
| `SparseAutoencoder` | SAE with encode/decode/forward/loss/train_step |
| `train_sae` | Convenience trainer with mini-batch SGD |
| `analyze_features` | Feature activation statistics and ranking |

## References

- Elhage et al. 2022 -- Toy Models of Superposition
- Cunningham et al. 2023 -- Sparse Autoencoders Find Interpretable Features

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
