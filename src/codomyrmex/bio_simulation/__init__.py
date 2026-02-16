"""Bio-Simulation Module for Codomyrmex.

Provides ant colony simulation with pheromone-based foraging and
genomics / genetic algorithm integration.
"""

from .ant_colony import Ant, AntState, Colony, Environment
from .genomics import Genome, Population

__all__ = [
    "Ant",
    "AntState",
    "Colony",
    "Environment",
    "Genome",
    "Population",
]
