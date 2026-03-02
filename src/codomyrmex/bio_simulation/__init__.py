"""Bio-Simulation Module for Codomyrmex.

Provides ant colony simulation with pheromone-based foraging and
genomics / genetic algorithm integration.
"""

from .ant_colony.ant import Ant, AntState
from .ant_colony.colony import Colony
from .ant_colony.environment import Environment
from .genomics.genome import Genome
from .genomics.population import Population

__all__ = [
    "Ant",
    "AntState",
    "Colony",
    "Environment",
    "Genome",
    "Population",
]
