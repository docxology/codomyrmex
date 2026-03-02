"""Evolutionary AI module for Codomyrmex.

Provides genetic algorithm components:
- Genome and Individual representation
- Population management
- Genetic Operators (Mutation, Crossover)
- Selection Strategies
- Fitness Evaluation Framework
"""

from .genome.genome import Genome, Individual, GenomeStats
from .population.population import Population, GenerationStats
from .operators.operators import (
    MutationOperator,
    BitFlipMutation,
    SwapMutation,
    GaussianMutation,
    ScrambleMutation,
    CrossoverOperator,
    SinglePointCrossover,
    TwoPointCrossover,
    UniformCrossover,
    BlendCrossover,
)
from .selection.selection import (
    SelectionOperator,
    TournamentSelection,
    RouletteWheelSelection,
    RankSelection,
)
from .fitness.fitness import (
    FitnessFunction,
    FitnessResult,
    ScalarFitness,
    MultiObjectiveFitness,
    ConstrainedFitness,
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
