# Evolutionary AI Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Evolutionary AI module provides genetic algorithm components for automated optimization within Codomyrmex. It includes genome representation, population management, and a comprehensive suite of selection, crossover, and mutation operators. The module supports both simple evolutionary workflows through convenience functions and advanced use cases through extensible operator classes.

## Key Features

- **Genome Representation**: Flexible genome class with float-valued gene encoding and fitness tracking
- **Population Management**: Population class with evaluation, selection, and generational evolution
- **Multiple Mutation Operators**: BitFlip, Swap, Gaussian, and Scramble mutation strategies
- **Multiple Crossover Operators**: SinglePoint, TwoPoint, Uniform, and Blend crossover strategies
- **Multiple Selection Operators**: Tournament, Roulette, Rank, and Elitism selection strategies
- **Factory Functions**: `create_mutation`, `create_crossover`, and `create_selection` for easy operator instantiation
- **Convenience Functions**: Top-level `crossover()`, `mutate()`, and `tournament_selection()` for quick use

## Key Components

| Component | Description |
|-----------|-------------|
| `Genome` | Genome representation with float-valued genes and fitness tracking |
| `Population` | Population management with evaluation, selection, and evolution methods |
| `Individual` | Individual representation imported from the operators submodule |
| `MutationType` | Enum defining available mutation strategies |
| `CrossoverType` | Enum defining available crossover strategies |
| `SelectionType` | Enum defining available selection strategies |
| `MutationOperator` | Base class for mutation operators |
| `BitFlipMutation` | Bit-flip mutation for binary-encoded genomes |
| `SwapMutation` | Swap mutation that exchanges gene positions |
| `GaussianMutation` | Gaussian perturbation mutation for continuous values |
| `ScrambleMutation` | Scramble mutation that shuffles gene subsequences |
| `CrossoverOperator` | Base class for crossover operators |
| `SinglePointCrossover` | Single-point crossover at a random position |
| `TwoPointCrossover` | Two-point crossover between two random positions |
| `UniformCrossover` | Uniform crossover with per-gene swap probability |
| `BlendCrossover` | Blend crossover for continuous-valued genomes |
| `SelectionOperator` | Base class for selection operators |
| `TournamentSelection` | Tournament-based selection |
| `RouletteSelection` | Fitness-proportionate roulette wheel selection |
| `RankSelection` | Rank-based selection |
| `ElitismSelection` | Elitism selection preserving top individuals |
| `create_mutation` | Factory function to create mutation operators by type |
| `create_crossover` | Factory function to create crossover operators by type |
| `create_selection` | Factory function to create selection operators by type |
| `crossover` | Convenience function for single-point crossover |
| `mutate` | Convenience function for Gaussian mutation |
| `tournament_selection` | Convenience function for tournament selection |
| `operators` | Submodule with all operator implementations |
| `selection` | Submodule for selection-specific logic |
| `fitness` | Submodule for fitness evaluation functions |

## Quick Start

```python
from codomyrmex.evolutionary_ai import Genome, Population, crossover, mutate

# Create a population
pop = Population(size=50, genome_length=20)

# Define a fitness function
def fitness_fn(genome: Genome) -> float:
    return sum(genome.genes)

# Evaluate and evolve
pop.evaluate(fitness_fn)
pop.evolve(mutation_rate=0.05, crossover_rate=0.8, elitism=2)

best = pop.get_best()
print(f"Best fitness: {best.fitness}")
```

### Using Operator Classes

```python
from codomyrmex.evolutionary_ai import (
    create_mutation, create_crossover, create_selection,
    MutationType, CrossoverType, SelectionType,
)

mutation = create_mutation(MutationType.GAUSSIAN)
crossover_op = create_crossover(CrossoverType.UNIFORM)
selection = create_selection(SelectionType.TOURNAMENT)
```

## Architecture

The module is organized into five subpackages:

```
evolutionary_ai/
  operators/    # Mutation, crossover, and selection operator implementations
  selection/    # Selection-specific logic
  fitness/      # Fitness evaluation functions
  genome/       # Genome representation (optional)
  population/   # Population management (optional)
```

## Related Modules

- [inference_optimization](../inference_optimization/) - Optimization techniques that may complement evolutionary search
- [pattern_matching](../pattern_matching/) - Pattern recognition that can feed fitness evaluation

## Navigation

- **Source**: [src/codomyrmex/evolutionary_ai/](../../../src/codomyrmex/evolutionary_ai/)
- **API Specification**: [src/codomyrmex/evolutionary_ai/API_SPECIFICATION.md](../../../src/codomyrmex/evolutionary_ai/API_SPECIFICATION.md)
- **Parent**: [docs/modules/](../README.md)
