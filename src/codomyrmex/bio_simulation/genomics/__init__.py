"""Genomics subpackage for bio simulation.

Provides genetic algorithms with genome representation, mutation,
crossover, and population-level evolution.
"""

from .genome import Genome, Population

__all__ = ["Genome", "Population"]
