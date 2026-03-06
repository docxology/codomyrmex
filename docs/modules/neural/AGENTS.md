# Neural Network Primitives -- Agent Coordination

**Version**: v1.1.6 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides from-scratch Transformer implementation including multi-head attention, flash attention, feed-forward networks, layer normalization, positional encoding, and activation functions. All implemented in pure NumPy.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `transformer_encode` | Run a forward pass through a randomly-initialized Transformer encoder | Standard | neural |
| `attention_forward` | Run multi-head attention on random inputs and return attention weights | Standard | neural |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Construct and evaluate neural network components from scratch |
| VERIFY | QA Agent | Validate attention patterns and transformer output shapes |


## Agent Instructions

1. d_model must be divisible by n_heads for proper head dimension calculation
2. Flash attention verifies against standard attention within a tight error tolerance


## Navigation

- [Source README](../../src/codomyrmex/neural/README.md) | [SPEC.md](SPEC.md)
