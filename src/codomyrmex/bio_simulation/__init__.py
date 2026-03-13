"""Bio-Simulation Module for Codomyrmex.

Provides ant colony simulation with pheromone-based foraging and
genomics / genetic algorithm integration.
"""

from .ant_colony.ant import Ant, AntState
from .ant_colony.colony import Colony
from .ant_colony.environment import Environment
from .cellular import CellularAutomaton
from .genomics.genome import Genome
from .genomics.population import Population
from .reactor import BioReactor, Metabolite, Reaction

__all__ = [
    "Ant",
    "AntState",
    "BioReactor",
    "CellularAutomaton",
    "Colony",
    "Environment",
    "Genome",
    "Metabolite",
    "Population",
    "Reaction",
]
