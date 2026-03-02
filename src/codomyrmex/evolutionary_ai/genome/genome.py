"""Genome and Individual definitions for evolutionary algorithms.

Provides a generic Individual class and a float-vector Genome subclass
with fitness tracking, distance metrics, serialization, and random initialization.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class Individual(Generic[T]):
    """An individual in the population.

    Attributes:
        genes: The genetic material.
        fitness: Fitness score assigned after evaluation (None if unevaluated).
        metadata: Optional dict for storing additional information (e.g. lineage).
    """

    genes: T
    fitness: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other: Individual[T]) -> bool:
        """Compare individuals by fitness for sorting.

        Unevaluated individuals are considered "less fit" than evaluated ones.
        """
        if self.fitness is None and other.fitness is None:
            return False
        if self.fitness is None:
            return True
        if other.fitness is None:
            return False
        return self.fitness < other.fitness

    def __eq__(self, other: object) -> bool:
        """Check equality based on genes."""
        if not isinstance(other, Individual):
            return NotImplemented
        return self.genes == other.genes


@dataclass
class GenomeStats:
    """Summary statistics for a genome's gene values."""

    mean: float
    std: float
    min_val: float
    max_val: float
    length: int


class Genome(Individual[list[float]]):
    """Represents an individual's genetic information as a float vector.

    Inherits from Individual[list[float]].
    """

    # ── Factory methods ─────────────────────────────────────────────

    @classmethod
    def random(cls, length: int, low: float = 0.0, high: float = 1.0) -> Genome:
        """Create a random genome with genes uniformly distributed in [low, high]."""
        return cls(genes=[random.uniform(low, high) for _ in range(length)])

    @classmethod
    def zeros(cls, length: int) -> Genome:
        """Create a genome of all zeros."""
        return cls(genes=[0.0] * length)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Genome:
        """Reconstruct a Genome from a serialized dict."""
        return cls(
            genes=list(data["genes"]),
            fitness=data.get("fitness"),
            metadata=data.get("metadata", {}),
        )

    # ── Core operations ─────────────────────────────────────────────

    def clone(self) -> Genome:
        """Return an independent deep copy."""
        return Genome(
            genes=list(self.genes),
            fitness=self.fitness,
            metadata=dict(self.metadata),
        )

    def distance(self, other: Genome) -> float:
        """Euclidean distance between this genome and another.

        Raises:
            ValueError: If genome lengths differ.
        """
        if len(self.genes) != len(other.genes):
            raise ValueError(
                f"Cannot compute distance between genomes of length "
                f"{len(self.genes)} and {len(other.genes)}"
            )
        return math.sqrt(
            sum((a - b) ** 2 for a, b in zip(self.genes, other.genes, strict=False))
        )

    def clamp(self, low: float = 0.0, high: float = 1.0) -> Genome:
        """Return a new genome with genes clamped to [low, high]."""
        return Genome(
            genes=[max(low, min(high, g)) for g in self.genes],
            fitness=None,
            metadata=dict(self.metadata),
        )

    def stats(self) -> GenomeStats:
        """Compute summary statistics for the gene values."""
        n = len(self.genes)
        if n == 0:
            return GenomeStats(mean=0.0, std=0.0, min_val=0.0, max_val=0.0, length=0)
        mean = sum(self.genes) / n
        variance = sum((g - mean) ** 2 for g in self.genes) / n
        return GenomeStats(
            mean=mean,
            std=math.sqrt(variance),
            min_val=min(self.genes),
            max_val=max(self.genes),
            length=n,
        )

    # ── Serialization ───────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dict."""
        return {
            "genes": list(self.genes),
            "fitness": self.fitness,
            "metadata": self.metadata,
        }

    # ── Dunder methods ──────────────────────────────────────────────

    def __len__(self) -> int:
        """Return the number of items."""
        return len(self.genes)

    def __getitem__(self, index: int) -> float:
        """Return item at the given index."""
        return self.genes[index]

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Genome(fitness={self.fitness}, length={len(self)})"
