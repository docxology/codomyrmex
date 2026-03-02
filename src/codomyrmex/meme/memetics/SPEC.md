# Memetics -- Technical Specification

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Overview

Core memetic engine providing data structures and algorithms for modeling memes as discrete replicable information units. Implements fitness evaluation, mutation operators (semantic drift, recombination, splicing), evolutionary selection, and population-level analysis. Memes have fidelity, fecundity, and longevity attributes that determine their composite fitness.

## Architecture

Evolutionary computation pattern. `Meme` objects have content, type classification, and three fitness dimensions. `Memeplex` groups co-adapted memes with synergy bonuses. `MemeticEngine` provides text dissection, synthesis, fitness landscape computation, and evolutionary selection (tournament or truncation). Mutation operators in `mutation.py` apply content-level perturbations while tracking lineage.

## Key Classes

### `MemeticEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `dissect` | `text: str` | `list[Meme]` | Split text into sentence-level memes, classify by keyword heuristics |
| `synthesize` | `memes: list[Meme], separator: str` | `str` | Join meme contents into coherent text |
| `fitness_landscape` | `population: list[Memeplex]` | `FitnessMap` | Compute fitness map for a memeplex population |
| `select` | `population: list[Memeplex], n, method` | `list[Memeplex]` | Tournament or truncation selection of fittest memeplexes |
| `evolve` | `population: list[Memeplex], generations, mutation_rate` | `list[Memeplex]` | Run evolutionary selection across multiple generations |

### `Meme`

| Method / Property | Parameters | Returns | Description |
|-------------------|-----------|---------|-------------|
| `fitness` | (property) | `float` | Geometric mean of fidelity, fecundity, longevity |
| `descend` | `new_content: str, **overrides` | `Meme` | Create mutated descendant preserving lineage |

### `Memeplex`

| Method / Property | Parameters | Returns | Description |
|-------------------|-----------|---------|-------------|
| `fitness` | (property) | `float` | Mean meme fitness multiplied by synergy bonus |
| `robustness_score` | none | `float` | Gini-coefficient-based uniformity measure |
| `mutate` | `mutation_rate: float` | `Memeplex` | Create mutated copy with Gaussian perturbation |
| `recombine` | `other: Memeplex` | `Memeplex` | Crossover at random point to produce offspring |

### Data Models

| Class | Fields | Purpose |
|-------|--------|---------|
| `Meme` | `content, meme_type, fidelity, fecundity, longevity, lineage, id, created_at` | Discrete replicable information unit |
| `MemeType` | `BELIEF, NORM, STRATEGY, AESTHETIC, NARRATIVE, SYMBOL, RITUAL, SLOGAN` | Cognitive function classification |
| `MemeticCode` | `sequence: list[Meme]` | Ordered meme sequence with `splice_in`, `excise`, `aggregate_fitness` |
| `Memeplex` | `name, memes, synergy, id` | Co-adapted meme complex with synergy bonus |
| `FitnessMap` | `entries: dict[str, float], timestamp` | Population fitness snapshot with `mean_fitness`, `max_fitness`, `top_n` |

### Mutation Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `semantic_drift` | `meme: Meme, intensity: float` | `Meme` | Apply token-level perturbation markers, reduce fidelity |
| `recombine` | `meme_a, meme_b, crossover_point` | `Meme` | Content crossover with averaged properties |
| `splice` | `host: Meme, insert: Meme, position` | `Meme` | Horizontal gene transfer -- inject foreign content |
| `batch_mutate` | `population, mutation_rate, intensity` | `list[Meme]` | Apply mutations to population at given rate |

### Fitness Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `virality_score` | `meme: Meme, network_size: int` | `float` | Estimate virality from fecundity, brevity, and network scaling |
| `robustness_score` | `memeplex: Memeplex` | `float` | Coefficient-of-variation based robustness metric |
| `decay_rate` | `meme: Meme, half_life_days: float` | `float` | Exponential decay constant adjusted by longevity |
| `population_fitness_stats` | `population: list[Meme]` | `dict` | Summary stats: mean, std, min, max, count |

## Dependencies

- **Internal**: None (self-contained within `meme` package)
- **External**: Standard library only (`hashlib`, `time`, `uuid`, `math`, `random`, `re`)

## Constraints

- Meme fitness dimensions (fidelity, fecundity, longevity) are clamped to [0, 1] in `__post_init__`.
- Meme IDs are SHA-256 hashes truncated to 16 characters; not guaranteed collision-free at scale.
- Type classification uses simple keyword matching (no NLP); defaults to `BELIEF` when no keywords match.
- `evolve` currently uses cloning instead of crossover recombination for offspring generation.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `dissect` returns empty list for empty input.
- `select` returns empty list for empty population.
- `population_fitness_stats` returns zeroed dict for empty population.
