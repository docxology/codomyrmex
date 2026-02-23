# Evolutionary AI Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The evolutionary_ai module provides a complete genetic algorithm framework for evolutionary optimization. It includes genome representation with float-valued genes, population management with elitism-preserving evolution, and a rich library of pluggable operators for mutation (bit-flip, swap, Gaussian, scramble), crossover (single-point, two-point, uniform, blend), and selection (tournament, roulette, rank, elitism) -- all accessible via factory functions.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Core Classes

- **`Genome`** -- Represents an individual's genetic material as a list of float genes (0-1 range). Supports random initialization, copying, indexing, and iteration. Tracks fitness score.
- **`Population`** -- Manages a collection of `Genome` individuals with methods for `evaluate()` (apply fitness function), `get_best()` / `get_worst()`, and `evolve()` with configurable mutation rate, crossover rate, and elitism count.
- **`Individual`** -- Alternative individual representation from the operators submodule.

### Convenience Functions

- **`crossover()`** -- Perform single-point crossover between two genomes, returning two child genomes.
- **`mutate()`** -- Apply Gaussian mutation to a genome with configurable per-gene mutation rate, clamping values to [0, 1].
- **`tournament_selection()`** -- Select an individual from a population using tournament selection with configurable tournament size (default 3).

### Operator Type Enums

- **`MutationType`** -- Enum of available mutation types
- **`CrossoverType`** -- Enum of available crossover types
- **`SelectionType`** -- Enum of available selection types

### Mutation Operators

- **`MutationOperator`** -- Abstract base class for mutation operators
- **`BitFlipMutation`** -- Flips bits in binary-encoded genomes
- **`SwapMutation`** -- Swaps two random gene positions
- **`GaussianMutation`** -- Adds Gaussian noise to gene values
- **`ScrambleMutation`** -- Randomly reorders a segment of the genome

### Crossover Operators

- **`CrossoverOperator`** -- Abstract base class for crossover operators
- **`SinglePointCrossover`** -- Crosses parents at a single random point
- **`TwoPointCrossover`** -- Crosses parents between two random points
- **`UniformCrossover`** -- Each gene independently selected from either parent
- **`BlendCrossover`** -- Blends parent gene values using interpolation

### Selection Operators

- **`SelectionOperator`** -- Abstract base class for selection operators
- **`TournamentSelection`** -- Selects winners from random tournament subsets
- **`RouletteSelection`** -- Probability of selection proportional to fitness
- **`RankSelection`** -- Selection probability based on fitness rank ordering
- **`ElitismSelection`** -- Directly preserves the top-performing individuals

### Factory Functions

- **`create_mutation()`** -- Create a mutation operator by type enum
- **`create_crossover()`** -- Create a crossover operator by type enum
- **`create_selection()`** -- Create a selection operator by type enum

### Submodules

- **`operators`** -- All operator implementations and type enums
- **`selection`** -- Extended selection strategy implementations
- **`fitness`** -- Fitness function definitions and evaluation utilities

## Directory Contents

- `__init__.py` - Module entry point with `Genome`, `Population`, convenience functions, and all operator exports
- `operators/` - Mutation, crossover, and selection operator implementations with type enums and factory functions
- `selection/` - Extended selection strategy implementations
- `fitness/` - Fitness function definitions and evaluation utilities
- `genome/` - Extended genome representations
- `population/` - Extended population management utilities
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Quick Start

```python
from codomyrmex.evolutionary_ai import Genome, Population

# Initialize Genome
instance = Genome()
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k evolutionary_ai -v
```

## Navigation

- **Full Documentation**: [docs/modules/evolutionary_ai/](../../../docs/modules/evolutionary_ai/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
