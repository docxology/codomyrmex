"""Evolutionary AI module for Codomyrmex.

Provides genetic algorithm components:
- Genome and Individual representation
- Population management
- Genetic Operators (Mutation, Crossover)
- Selection Strategies
- Fitness Evaluation Framework
"""

from .fitness.fitness import (
    ConstrainedFitness,
    FitnessFunction,
    FitnessResult,
    MultiObjectiveFitness,
    ScalarFitness,
)
from .genome.genome import Genome, GenomeStats, Individual
from .operators.operators import (
    BitFlipMutation,
    BlendCrossover,
    CrossoverOperator,
    GaussianMutation,
    MutationOperator,
    ScrambleMutation,
    SinglePointCrossover,
    SwapMutation,
    TwoPointCrossover,
    UniformCrossover,
)
from .population.population import GenerationStats, Population
from .selection.selection import (
    RankSelection,
    RouletteWheelSelection,
    SelectionOperator,
    TournamentSelection,
)

__all__ = [
    # Core types
    "Individual",
    "Genome",
    "GenomeStats",
    "Population",
    "GenerationStats",

    # Operators
    "MutationOperator",
    "BitFlipMutation",
    "SwapMutation",
    "GaussianMutation",
    "ScrambleMutation",
    "CrossoverOperator",
    "SinglePointCrossover",
    "TwoPointCrossover",
    "UniformCrossover",
    "BlendCrossover",

    # Selection
    "SelectionOperator",
    "TournamentSelection",
    "RouletteWheelSelection",
    "RankSelection",

    # Fitness
    "FitnessFunction",
    "FitnessResult",
    "ScalarFitness",
    "MultiObjectiveFitness",
    "ConstrainedFitness",
]

__version__ = "1.1.0"
