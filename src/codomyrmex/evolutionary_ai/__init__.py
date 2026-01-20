"""Evolutionary AI module for Codomyrmex."""

from .genome import Genome
from .operators import crossover, mutate, tournament_selection
from .population import Population

__all__ = [
    "Genome",
    "crossover",
    "mutate",
    "tournament_selection",
    "Population",
]

__version__ = "0.1.0"
