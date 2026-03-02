"""Genomics subpackage for bio simulation.

Provides genetic algorithms with genome representation, mutation,
crossover, and population-level evolution.
"""

from .genome import Genome
from .population import Population

__all__ = ["Genome", "Population"]
