# Model Merger - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Merge neural network model parameters using mathematically principled interpolation methods for model combination and ensembling.

## Functional Requirements

- SLERP interpolation preserving angular direction on hypersphere
- Linear parameter interpolation with configurable alpha
- Model soup (weighted average) of arbitrary number of models
- Automatic magnitude preservation in SLERP
- Fallback to linear interpolation for nearly-parallel vectors

## Core Functions

| Function | Description |
|----------|-------------|
| `slerp(v0, v1, t)` | Spherical linear interpolation between vectors |
| `linear_interpolate(a, b, alpha)` | Linear blend of parameter dicts |
| `model_soup(dicts, weights)` | Weighted average of multiple models |

## SLERP Mathematics

```
slerp(v0, v1, t) = sin((1-t)*omega)/sin(omega) * v0 + sin(t*omega)/sin(omega) * v1
where omega = arccos(v0_hat . v1_hat)
```

When sin(omega) approaches 0 (parallel vectors), SLERP degrades to linear interpolation.

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
