# NAS - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `nas` module provides Neural Architecture Search over configurable architecture spaces. Supports random search and evolutionary search strategies for discovering optimal network architectures.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `NASSearcher` | Orchestrates the architecture search process |
| `NASSearchSpace` | Defines the architecture space (layer types, widths, depths) |
| `ArchConfig` | A single architecture configuration sampled from the search space |

### 2.2 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `random_search` | `(space, n_trials, eval_fn) -> ArchConfig` | Random search over the architecture space |
| `evolutionary_search` | `(space, pop_size, generations, eval_fn) -> ArchConfig` | Evolutionary search with mutation and crossover |

## 3. Usage Example

```python
from codomyrmex.nas import NASSearchSpace, random_search

space = NASSearchSpace(
    layer_types=["conv", "linear", "attention"],
    depth_range=(2, 8),
    width_range=(32, 512),
)

best = random_search(space, n_trials=100, eval_fn=lambda arch: arch.score())
print(f"Best architecture: {best}")
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
