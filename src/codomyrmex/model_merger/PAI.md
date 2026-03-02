# Personal AI Infrastructure -- Model Merger Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Model Merger module provides SLERP interpolation, linear interpolation, and model soups
for combining neural network parameters. Used in ML workflows to merge fine-tuned checkpoints,
create model ensembles, and explore the loss landscape between trained models.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `codomyrmex.merge_models` | Merge two models with SLERP or linear interpolation | Safe | model_merger |
| `codomyrmex.create_model_soup` | Average multiple models into a soup | Safe | model_merger |

## PAI Algorithm Phase Mapping

| Phase | Contribution | Key Functions |
|-------|-------------|---------------|
| **BUILD** (4/7) | Merge fine-tuned checkpoints | `ModelMerger.merge()`, `merge_models` MCP |
| **THINK** (2/7) | Evaluate merge strategies | `slerp()`, `linear_interpolate()` |
| **VERIFY** (6/7) | Validate merged model parameters | `model_soup()` for ensemble validation |

## Architecture Role

**Application Layer** -- Pure NumPy model merging consumed by ML training workflows.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
- **MCP Tools**: [mcp_tools.py](mcp_tools.py)
