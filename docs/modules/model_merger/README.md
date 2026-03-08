# Model Merger Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `model_merger` module provides model weight merging utilities including SLERP (Spherical Linear Interpolation), linear interpolation, and model soups (Wortsman et al. 2022). These techniques combine multiple fine-tuned models into a single model that often outperforms individual models by smoothing out loss basin differences. All operations work on dictionaries of NumPy arrays representing model parameters. Pure Python and NumPy -- no PyTorch dependency.

## Architecture

The module is contained in `merger.py` with three functions and one class:

- **`slerp()`** -- spherical interpolation along a hypersphere arc, with fallback to linear interpolation when vectors are nearly parallel
- **`linear_interpolate()`** -- weighted average of two parameter dictionaries
- **`model_soup()`** -- weighted average across N models (uniform weights by default)
- **`ModelMerger`** -- high-level class with configurable merge method ("slerp" or "linear")

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `ModelMerger` | `merger.py` | High-level merger with configurable method (slerp/linear) |
| `slerp` | `merger.py` | Spherical linear interpolation preserving vector magnitude |
| `linear_interpolate` | `merger.py` | Linear interpolation: (1-alpha)*A + alpha*B |
| `model_soup` | `merger.py` | Weighted average of N models (Wortsman et al. 2022) |

## Quick Start

```python
import numpy as np
from codomyrmex.model_merger import ModelMerger, slerp, model_soup

# Two fine-tuned model parameter dicts
model_a = {"layer1.weight": np.random.randn(256, 256)}
model_b = {"layer1.weight": np.random.randn(256, 256)}

# SLERP merge (preserves weight magnitude better than linear)
merger = ModelMerger(method="slerp")
merged = merger.merge(model_a, model_b, alpha=0.5)

# Model soup: average 3 fine-tuned models
model_c = {"layer1.weight": np.random.randn(256, 256)}
soup = model_soup([model_a, model_b, model_c], weights=[0.4, 0.3, 0.3])
```

## Merge Methods

| Method | Formula | Best For |
|--------|---------|----------|
| SLERP | Interpolate along hypersphere arc | Unit-normalized weight vectors |
| Linear | (1-alpha)*A + alpha*B | General-purpose blending |
| Model Soup | Weighted average of N models | Ensembling multiple fine-tunes |

SLERP falls back to linear interpolation when vectors are nearly parallel (sin(omega) near 0). It also preserves original magnitude via linear interpolation of norms.

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| BUILD | Combine multiple fine-tuned models into one |
| EXECUTE | Merge LoRA/PEFT adapted weights back into base models |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/model_merger/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports: ModelMerger, slerp, linear_interpolate, model_soup |
| `merger.py` | All merging algorithms and ModelMerger class |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [lora](../lora/) -- LoRA weights that need merging into base models
- [peft](../peft/) -- PEFT adapters whose weights can be merged
- [neural](../neural/) -- Transformer weights that merging operates on

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/model_merger/`](../../../src/codomyrmex/model_merger/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)
