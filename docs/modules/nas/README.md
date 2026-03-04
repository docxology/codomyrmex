# NAS (Neural Architecture Search) Module

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `nas` module provides a neural architecture search framework with random and evolutionary search strategies over transformer-like architecture spaces. It defines a configurable search space of layer counts, model dimensions, head counts, feed-forward multipliers, dropout rates, and activation functions. The evaluation function is pluggable, making it a general-purpose NAS framework. Pure Python and NumPy -- no PyTorch dependency.

## Architecture

The module is contained in `search.py` with three main components:

- **`NASSearchSpace`** -- defines searchable dimensions with default ranges
- **`ArchConfig`** -- a sampled architecture configuration with parameter count estimation
- **`NASSearcher`** -- search engine with random search and evolutionary search (mutation-based)

The evolutionary search uses tournament selection (top-half survival) with single-dimension mutation per generation.

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `NASSearchSpace` | `search.py` | Defines searchable architecture dimensions with `sample()` and `validate()` |
| `ArchConfig` | `search.py` | Sampled architecture config with `total_params_estimate` property |
| `NASSearcher` | `search.py` | Search engine with `random_search()` and `evolutionary_search()` |
| `random_search` | `search.py` | Standalone random search function |
| `evolutionary_search` | `search.py` | Standalone evolutionary search function |

## Quick Start

```python
import numpy as np
from codomyrmex.nas import NASSearchSpace, NASSearcher, ArchConfig

# Define search space (defaults cover typical transformer configs)
space = NASSearchSpace(
    n_layers=[2, 4, 6, 8],
    d_model=[128, 256, 512],
    n_heads=[4, 8],
)

# Pluggable evaluation function (replace with real training)
def eval_fn(config: ArchConfig) -> float:
    # Prefer smaller models (negative param count as score)
    return -config.total_params_estimate / 1e6

# Run evolutionary search
searcher = NASSearcher(space, eval_fn)
best = searcher.evolutionary_search(n_generations=5, population_size=10)
print(f"Best: {best.n_layers} layers, d_model={best.d_model}, "
      f"~{best.total_params_estimate:,} params")
```

## Search Space Defaults

| Dimension | Default Values |
|-----------|---------------|
| `n_layers` | [1, 2, 4, 6, 8] |
| `d_model` | [64, 128, 256, 512] |
| `n_heads` | [2, 4, 8] |
| `d_ff_multiplier` | [2, 4, 8] |
| `dropout` | [0.0, 0.1, 0.3] |
| `activation` | ["relu", "gelu", "swish"] |

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| PLAN | Automated architecture selection before training |
| BUILD | Search for optimal model configurations |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/nas/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports: NASSearchSpace, ArchConfig, NASSearcher, random_search, evolutionary_search |
| `search.py` | Search space, architecture config, and search algorithms |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [neural](../neural/) -- Transformer primitives searched over by NAS |
- [slm](../slm/) -- Small Language Models whose architecture NAS can optimize |
- [performance](../../modules/performance/) -- Benchmarking for NAS evaluation functions |

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/nas/`](../../../src/codomyrmex/nas/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)
