"""
Fitness evaluation for evolutionary algorithms.

Provides an abstract FitnessFunction base class and concrete implementations
for scalar, multi-objective (Pareto), and constrained fitness evaluation.
"""

from .fitness import (
    ConstrainedFitness,
    FitnessFunction,
    FitnessResult,
    MultiObjectiveFitness,
    ScalarFitness,
)

__all__ = [
    "ConstrainedFitness",
    "FitnessFunction",
    "FitnessResult",
    "MultiObjectiveFitness",
    "ScalarFitness",
]
