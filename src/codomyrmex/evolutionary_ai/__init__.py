"""Evolutionary AI module for Codomyrmex."""

from .genome.genome import Genome
from .operators.operators import crossover, mutate, tournament_selection
from .population.population import Population

# Submodule exports
from . import genome
from . import operators
from . import population
from . import selection
from . import fitness

__all__ = [
    "Genome",
    "crossover",
    "mutate",
    "tournament_selection",
    "Population",
    "genome",
    "operators",
    "population",
    "selection",
    "fitness",
]

__version__ = "0.1.0"

