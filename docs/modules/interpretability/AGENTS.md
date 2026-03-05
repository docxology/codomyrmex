# Interpretability -- Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides Sparse Autoencoder (SAE) tools for mechanistic interpretability of neural networks. Trains SAEs on activation data to discover interpretable sparse features and analyze activation patterns.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `sae_train` | Train a Sparse Autoencoder on activation data for mechanistic interpretability | Standard | interpretability |
| `sae_analyze` | Analyze features learned by a Sparse Autoencoder on provided activations | Standard | interpretability |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| OBSERVE | Research Agent | Analyze neural network internals via sparse feature decomposition |
| VERIFY | QA Agent | Validate interpretability results against expected feature patterns |


## Agent Instructions

1. d_features defaults to 4x d_input for overcomplete dictionary learning
2. lambda_l1 controls sparsity penalty -- higher values produce sparser features


## Navigation

- [Source README](../../src/codomyrmex/interpretability/README.md) | [SPEC.md](SPEC.md)
