# Genome Representation -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Dual genome implementations: an ABC hierarchy for typed genomes used by operator ABCs, and a concrete float-vector `Genome` class used by function-based operators.

## Architecture

```
genome/
├── __init__.py   # Genome ABC, BinaryGenome, RealValuedGenome, PermutationGenome
└── genome.py     # Concrete Genome (float vector), GenomeStats
```

## Key Classes

### Genome (ABC, `__init__.py`)

| Method | Signature | Description |
|--------|-----------|-------------|
| `copy` | `() -> Genome` | Deep copy of genome |
| `to_list` | `() -> list` | Export gene values as list |

### BinaryGenome

| Field/Method | Type/Signature | Description |
|-------------|----------------|-------------|
| `bits` | `list[int]` | List of 0/1 values |
| `length` | `int` | Number of bits |
| `flip` | `(index: int) -> None` | Toggle bit at index |

### RealValuedGenome

| Field/Method | Type/Signature | Description |
|-------------|----------------|-------------|
| `values` | `list[float]` | Float gene values |
| `min_bound` | `float` | Lower bound for clamping |
| `max_bound` | `float` | Upper bound for clamping |
| `clip` | `() -> None` | Clamp all values to bounds |

### PermutationGenome

| Field/Method | Type/Signature | Description |
|-------------|----------------|-------------|
| `elements` | `list[Any]` | Ordered sequence |
| `swap` | `(i: int, j: int) -> None` | Exchange elements at positions i and j |

### Genome (`genome.py`)

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(genes: list[float], fitness: float = 0.0)` | Create genome with genes and fitness |
| `random` | `classmethod(length, low=0.0, high=1.0) -> Genome` | Random genome in range |
| `zeros` | `classmethod(length) -> Genome` | Zero-initialized genome |
| `from_dict` | `classmethod(data: dict) -> Genome` | Deserialize from dict |
| `clone` | `() -> Genome` | Deep copy |
| `distance` | `(other: Genome) -> float` | Euclidean distance |
| `clamp` | `(low: float, high: float) -> None` | Clamp genes to range |
| `stats` | `() -> GenomeStats` | Compute mean, std, min, max, length |
| `to_dict` | `() -> dict` | Serialize to dict |

### GenomeStats

Fields: `mean: float`, `std: float`, `min_val: float`, `max_val: float`, `length: int`.

## Dependencies

- Python standard library only (`math`, `random`, `statistics`).

## Navigation

- [README](../README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
