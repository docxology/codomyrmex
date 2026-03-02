"""Population management and evolution cycle.

Provides a ``Population`` class that manages a collection of individuals,
tracks generational statistics, detects convergence, and supports
configurable selection/crossover/mutation strategies.
"""
from .population import GenerationStats, Population

__all__ = [
    "Population",
    "GenerationStats",
]
