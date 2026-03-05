"""
Genome and Individual definitions for evolutionary algorithms.

Provides a generic Individual class and a float-vector Genome subclass
with fitness tracking, distance metrics, serialization, and random initialization.
"""

from .genome import Genome, GenomeStats, Individual

__all__ = [
    "Genome",
    "GenomeStats",
    "Individual",
]
