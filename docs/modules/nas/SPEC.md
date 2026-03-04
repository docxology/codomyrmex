# Neural Architecture Search Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides random and evolutionary search over neural architecture search spaces. Defines configurable architecture search spaces with sampling, evaluation, and best-architecture selection.

## Functional Requirements

1. Configurable NASSearchSpace with ranges for n_layers, d_model, n_heads, d_ff, dropout, activation
2. Random search with pluggable evaluation function and trial history
3. Evolutionary search with mutation, crossover, and tournament selection


## Interface

```python
from codomyrmex.nas import NASSearchSpace, NASSearcher, ArchConfig

space = NASSearchSpace()
config = space.sample(seed=42)
searcher = NASSearcher(space, eval_fn)
best = searcher.random_search(n_trials=100)
```

## Exports

NASSearchSpace, ArchConfig, NASSearcher, random_search, evolutionary_search

## Navigation

- [Source README](../../src/codomyrmex/nas/README.md) | [AGENTS.md](AGENTS.md)
