"""
Selection operators for evolutionary algorithms.

Provides an abstract SelectionOperator base class and concrete implementations
for tournament, roulette-wheel (fitness-proportionate), and rank-based
selection.
"""
from .selection import (
    RankSelection,
    RouletteWheelSelection,
    SelectionOperator,
    TournamentSelection,
)

__all__ = [
    "RankSelection",
    "RouletteWheelSelection",
    "SelectionOperator",
    "TournamentSelection",
]
