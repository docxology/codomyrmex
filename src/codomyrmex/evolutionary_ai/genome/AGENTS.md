# Codomyrmex Agents -- evolutionary_ai/genome

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Genome representations and encoding schemes for evolutionary computation, providing both abstract and concrete genome types.

## Key Components

| Component | Role |
|-----------|------|
| `Genome` (ABC, `__init__.py`) | Abstract base with `copy()` and `to_list() -> list` |
| `BinaryGenome` | Fixed-length bit string with `flip(index)` mutation helper |
| `RealValuedGenome` | Float vector with min/max bounds and `clip()` to enforce range |
| `PermutationGenome` | Ordered element list with `swap(i, j)` for order-based mutation |
| `Genome` (`genome.py`) | Concrete float-vector genome with `fitness`, `clone()`, `distance()`, `clamp()`, `stats()` |
| `GenomeStats` | Dataclass: `mean`, `std`, `min_val`, `max_val`, `length` |

## Operating Contracts

- `__init__.py` defines the ABC hierarchy (`Genome`, `BinaryGenome`, `RealValuedGenome`, `PermutationGenome`) used by the operator ABCs in `operators/__init__.py`.
- `genome.py` defines a separate concrete `Genome` class (float-vector) used by function-based operators in `operators/operators.py` and `population/population.py`.
- `BinaryGenome.flip(index)` toggles bit at `index` in-place; raises `IndexError` if out of range.
- `RealValuedGenome.clip()` clamps all values to `[min_bound, max_bound]`.
- `PermutationGenome.swap(i, j)` exchanges elements at positions `i` and `j` in-place.
- `Genome` (from `genome.py`) factory methods: `random(length, low, high)`, `zeros(length)`, `from_dict(data)`.
- `Genome.distance(other)` computes Euclidean distance between two genomes.

## Integration Points

- ABC genomes are consumed by operator ABCs in `evolutionary_ai/operators/__init__.py`.
- Concrete `Genome` from `genome.py` is consumed by function-based operators in `operators/operators.py` and `population/population.py`.
- Also re-exported by `bio_simulation/genomics/__init__.py`.

## Navigation

- [README](../README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- Parent: [evolutionary_ai](../README.md)
