# Interpretability -- MCP Tool Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `interpretability` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `interpretability` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `sae_train`

**Description**: Train a Sparse Autoencoder on activation data for mechanistic interpretability.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `d_input` | `int` | Yes | -- | Input activation dimensionality |
| `d_features` | `int` | No | `None` | Number of sparse features (defaults to 4x d_input) |
| `n_samples` | `int` | No | `200` | Number of random activation samples to generate |
| `n_steps` | `int` | No | `50` | Training steps |
| `lambda_l1` | `float` | No | `1e-3` | L1 sparsity penalty |
| `seed` | `int` | No | `None` | Random seed |

**Returns**: `dict[str, Any]` -- Dictionary with d_input, d_features, final_loss, analysis (top features, sparsity metrics), and status.

**Example**:
```python
from codomyrmex.interpretability.mcp_tools import sae_train

result = sae_train(d_input=64, d_features=256, n_steps=100, lambda_l1=0.01, seed=42)
```

---

### `sae_analyze`

**Description**: Analyze features learned by a Sparse Autoencoder on provided activations.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `d_input` | `int` | Yes | -- | Input dimensionality |
| `d_features` | `int` | No | `None` | Number of sparse features |
| `n_samples` | `int` | No | `200` | Number of activation samples |
| `seed` | `int` | No | `42` | Random seed |

**Returns**: `dict[str, Any]` -- Dictionary with feature analysis: top features, sparsity, activation frequencies, and status.

**Example**:
```python
from codomyrmex.interpretability.mcp_tools import sae_analyze

result = sae_analyze(d_input=128, d_features=512, n_samples=500, seed=42)
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- no destructive operations
- **PAI Phases**: OBSERVE (feature analysis), THINK (mechanistic interpretability)
- **Dependencies**: Requires `numpy` and internal `sae` module (SparseAutoencoder, train_sae, analyze_features)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
