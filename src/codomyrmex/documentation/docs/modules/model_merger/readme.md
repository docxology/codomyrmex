# Model Merger Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

SLERP interpolation, linear interpolation, and model soups for merging neural network parameters.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **BUILD** | Merge fine-tuned model checkpoints | `merge_models`, `create_model_soup` |
| **THINK** | Evaluate merge strategies for model combination | `merge_models` |

## Key Exports

### Functions

- **`slerp(v0, v1, t)`** -- Spherical Linear Interpolation between vectors
- **`linear_interpolate(params_a, params_b, alpha)`** -- Linear parameter interpolation
- **`model_soup(param_dicts, weights)`** -- Weighted average of multiple models (Wortsman et al. 2022)

### Classes

- **`ModelMerger`** -- High-level merge interface supporting slerp and linear methods

## Quick Start

```python
import numpy as np
from codomyrmex.model_merger import slerp, model_soup, ModelMerger

# SLERP between two weight vectors
v0 = np.array([1.0, 0.0, 0.0])
v1 = np.array([0.0, 1.0, 0.0])
merged = slerp(v0, v1, t=0.5)

# Model soup of three fine-tuned models
soup = model_soup([model_a_params, model_b_params, model_c_params])

# High-level API
merger = ModelMerger(method="slerp")
result = merger.merge(params_a, params_b, alpha=0.3)
```

## Directory Structure

- `merger.py` -- SLERP, linear interpolation, model soup, ModelMerger class
- `mcp_tools.py` -- MCP tool definitions
- `__init__.py` -- Public API re-exports

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/model_merger/ -v
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
