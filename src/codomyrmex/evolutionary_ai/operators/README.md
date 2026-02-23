# evolutionary_ai/operators

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Genetic operators for evolutionary AI. Provides mutation, crossover, and selection operators for genetic algorithms with a generic, type-parameterized design. Includes factory functions for creating operators by enum type.

## Key Exports

### Enums

- **`MutationType`** -- Mutation operator types: `BIT_FLIP`, `SWAP`, `SCRAMBLE`, `INVERSION`, `GAUSSIAN`, `UNIFORM`, `BOUNDARY`
- **`CrossoverType`** -- Crossover operator types: `SINGLE_POINT`, `TWO_POINT`, `UNIFORM`, `BLEND`, `ORDER`, `CYCLE`
- **`SelectionType`** -- Selection operator types: `TOURNAMENT`, `ROULETTE`, `RANK`, `STEADY_STATE`, `ELITISM`, `TRUNCATION`

### Data Class

- **`Individual`** -- A generic individual in the population with typed genes (`T`), optional fitness score, and metadata. Supports comparison by fitness via `__lt__`

### Mutation Operators (ABC: `MutationOperator`)

- **`MutationOperator`** -- ABC with configurable `mutation_rate` and abstract `mutate()` method
- **`BitFlipMutation`** -- Bit flip mutation for binary gene representations (List[int])
- **`SwapMutation`** -- Swap mutation for permutation-based representations; swaps two random positions
- **`GaussianMutation`** -- Gaussian noise mutation for real-valued genes (List[float]) with configurable sigma and optional bounds clamping
- **`ScrambleMutation`** -- Scramble mutation that shuffles a random contiguous subset of genes

### Crossover Operators (ABC: `CrossoverOperator`)

- **`CrossoverOperator`** -- ABC with configurable `crossover_rate` and abstract `crossover()` method returning a pair of offspring
- **`SinglePointCrossover`** -- Classic single-point crossover splitting genes at one random point
- **`TwoPointCrossover`** -- Two-point crossover exchanging the segment between two random points
- **`UniformCrossover`** -- Gene-by-gene crossover with configurable mixing ratio
- **`BlendCrossover`** -- BLX-alpha crossover for real-valued genes, sampling offspring from an expanded range around parents

### Selection Operators (ABC: `SelectionOperator`)

- **`SelectionOperator`** -- ABC with abstract `select()` method
- **`TournamentSelection`** -- Tournament selection with configurable tournament size
- **`RouletteSelection`** -- Fitness-proportionate (roulette wheel) selection with automatic negative-fitness handling
- **`RankSelection`** -- Rank-based selection with configurable selection pressure
- **`ElitismSelection`** -- Always preserves the top N individuals (elite), fills remaining slots via a base selector (default: tournament)

### Factory Functions

- **`create_mutation()`** -- Create a mutation operator by `MutationType` enum
- **`create_crossover()`** -- Create a crossover operator by `CrossoverType` enum
- **`create_selection()`** -- Create a selection operator by `SelectionType` enum

## Directory Contents

- `__init__.py` - All operator ABCs, concrete implementations, enums, and factory functions (507 lines)
- `operators.py` - Extended operator utilities
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [evolutionary_ai](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
