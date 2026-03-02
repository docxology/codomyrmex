# Agent Guidelines - Model Merger

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Merge neural network model parameters using SLERP interpolation, linear interpolation, or model soups.

## Key Classes and Functions

- **`slerp(v0, v1, t)`** -- Spherical Linear Interpolation (direction-preserving)
- **`linear_interpolate(params_a, params_b, alpha)`** -- Linear weight blending
- **`model_soup(param_dicts, weights)`** -- Weighted average of multiple models
- **`ModelMerger`** -- High-level merge API with method selection

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `merge_models` | Merge two model parameter sets with SLERP or linear interpolation | Safe |
| `create_model_soup` | Average multiple model parameter sets into a soup | Safe |

## Agent Instructions

1. **SLERP for direction** -- Use SLERP when angular interpolation matters (e.g., attention heads)
2. **Linear for simple blends** -- Use linear interpolation for straightforward parameter mixing
3. **Model soup for ensembles** -- Average 3+ fine-tuned checkpoints from the same base model
4. **Alpha tuning** -- Try alpha values 0.3, 0.5, 0.7 and evaluate downstream

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `merge_models`, `create_model_soup` | TRUSTED |
| **Researcher** | Full | Both tools -- model merging experiments | SAFE |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
