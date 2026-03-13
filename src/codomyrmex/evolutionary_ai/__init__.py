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
from .genetic import Chromosome, GeneticAlgorithm
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
from .optimizer import optimize_config
from .population.population import GenerationStats, Population
from .selection.selection import (
    RankSelection,
    RouletteWheelSelection,
    SelectionOperator,
    TournamentSelection,
)

__all__ = [
    "BitFlipMutation",
    "BlendCrossover",
    "ConstrainedFitness",
    "CrossoverOperator",
    # Fitness
    "FitnessFunction",
    "FitnessResult",
    "GaussianMutation",
    "GenerationStats",
    "GeneticAlgorithm",
    "Genome",
    "GenomeStats",
    # Core types
    "Individual",
    "MultiObjectiveFitness",
    # Operators
    "MutationOperator",
    "Population",
    "RankSelection",
    "RouletteWheelSelection",
    "ScalarFitness",
    "ScrambleMutation",
    # Selection
    "SelectionOperator",
    "SinglePointCrossover",
    "SwapMutation",
    "TournamentSelection",
    "TwoPointCrossover",
    "UniformCrossover",
    "optimize_config",
]

__version__ = "1.1.0"
