# Neural Architecture Search (NAS)

Random and evolutionary search over transformer architecture spaces.

## Overview

The nas module provides a framework for Neural Architecture Search with pluggable evaluation functions. It defines a search space over transformer-like architectures and implements random search and evolutionary search with mutation.

## Quick Start

```python
from codomyrmex.nas import NASSearchSpace, NASSearcher, ArchConfig

space = NASSearchSpace()

# Define evaluation function (higher = better)
def eval_fn(config: ArchConfig) -> float:
    # Prefer smaller models with more layers
    return config.n_layers / (config.total_params_estimate / 1e6)

searcher = NASSearcher(space, eval_fn)

# Random search
best = searcher.random_search(n_trials=50, seed=42)
print(f"Best: {best.n_layers} layers, d_model={best.d_model}")

# Evolutionary search
best_evo = searcher.evolutionary_search(n_generations=10, population_size=20)
print(f"Evolved: {best_evo.n_layers} layers, d_model={best_evo.d_model}")
```

### Convenience Functions

```python
from codomyrmex.nas import random_search, evolutionary_search, NASSearchSpace

space = NASSearchSpace()
eval_fn = lambda c: -c.total_params_estimate  # minimize params

best = random_search(space, eval_fn, n_trials=100)
best = evolutionary_search(space, eval_fn, n_generations=10)
```

## Search Space

| Dimension | Default Values |
|-----------|---------------|
| n_layers | [1, 2, 4, 6, 8] |
| d_model | [64, 128, 256, 512] |
| n_heads | [2, 4, 8] |
| d_ff_multiplier | [2, 4, 8] |
| dropout | [0.0, 0.1, 0.3] |
| activation | ["relu", "gelu", "swish"] |

Constraint: d_model must be divisible by n_heads.

## Dependencies

- `numpy` (core dependency)
