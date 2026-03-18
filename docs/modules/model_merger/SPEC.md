# Model Merger Specification

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides SLERP interpolation and model soup techniques for merging neural network parameter sets. Supports both pairwise model merging and multi-model averaging with configurable weights.

## Functional Requirements

1. SLERP (Spherical Linear Interpolation) between two parameter sets on the unit hypersphere
2. Linear interpolation as a simpler alternative to SLERP
3. Model soup: weighted averaging of multiple model checkpoints


## Interface

```python
from codomyrmex.model_merger import ModelMerger, slerp, linear_interpolate, model_soup

merger = ModelMerger(method="slerp")
merged = merger.merge(params_a, params_b, alpha=0.5)
soup = model_soup([params_a, params_b, params_c], weights=[0.5, 0.3, 0.2])
```

## Exports

slerp, linear_interpolate, model_soup, ModelMerger

## Navigation

- [Source README](../../src/codomyrmex/model_merger/README.md) | [AGENTS.md](AGENTS.md)
