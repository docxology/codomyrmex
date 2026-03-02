# Personal AI Infrastructure -- Interpretability Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Interpretability module provides Sparse Autoencoders (SAEs) for mechanistic interpretability.
SAEs decompose neural network activations (transformer residual streams) into sparse, overcomplete
bases of interpretable "features," enabling understanding of what neural networks have learned.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `codomyrmex.sae_train` | Train a Sparse Autoencoder on activation data | Safe | interpretability |
| `codomyrmex.sae_analyze` | Analyze SAE feature activation patterns | Safe | interpretability |

## PAI Algorithm Phase Mapping

| Phase | Contribution | Key Functions |
|-------|-------------|---------------|
| **THINK** (2/7) | Decompose activations into interpretable features | `SparseAutoencoder.encode()`, `sae_train` MCP |
| **VERIFY** (6/7) | Validate feature sparsity and reconstruction quality | `analyze_features()`, `sae_analyze` MCP |
| **LEARN** (7/7) | Discover what networks have learned | `analyze_features()` |

## Architecture Role

**Application Layer** -- Pure NumPy SAE implementation for interpretability research.
Consumed by ML analysis workflows for understanding model internals.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
- **MCP Tools**: [mcp_tools.py](mcp_tools.py)
