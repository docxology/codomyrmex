"""
Genome representations for evolutionary algorithms.

Provides typed genome classes for binary, real-valued, and permutation
encodings.  Each genome type includes factory methods for random
initialisation and deep-copy support.
"""

from __future__ import annotations

import copy
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, TypeVar

T = TypeVar("T", bound="Genome")


class Genome(ABC):
    """Abstract base class for genome representations."""

    @abstractmethod
    def copy(self: T) -> T:
        """Return a deep copy of this genome."""

    @abstractmethod
    def to_list(self) -> list[Any]:
        """Serialise the genome to a plain list."""


@dataclass
class BinaryGenome(Genome):
    """Fixed-length binary (0/1) genome.

    Attributes:
        bits: The binary gene sequence.
    """
    bits: list[int] = field(default_factory=list)

    @classmethod
    def random(cls, length: int) -> BinaryGenome:
        """Create a random binary genome of the given length.

        Args:
            length: Number of bits.

        Returns:
            A new BinaryGenome with randomly assigned 0/1 values.
        """
        return cls(bits=[random.randint(0, 1) for _ in range(length)])

    def copy(self) -> BinaryGenome:
        """Execute Copy operations natively."""
        return BinaryGenome(bits=list(self.bits))

    def to_list(self) -> list[int]:
        """Execute To List operations natively."""
        return list(self.bits)

    def __len__(self) -> int:
        """Execute   Len   operations natively."""
        return len(self.bits)

    def flip(self, index: int) -> None:
        """Flip the bit at the given index."""
        self.bits[index] = 1 - self.bits[index]


@dataclass
class RealValuedGenome(Genome):
    """Fixed-length real-valued genome with optional bounds.

    Attributes:
        values: The real-valued gene sequence.
        lower_bounds: Per-gene lower bounds (None means unbounded).
        upper_bounds: Per-gene upper bounds (None means unbounded).
    """
    values: list[float] = field(default_factory=list)
    lower_bounds: list[float] | None = None
    upper_bounds: list[float] | None = None

    @classmethod
    def random(
        cls,
        length: int,
        lower: float = 0.0,
        upper: float = 1.0,
    ) -> RealValuedGenome:
        """Create a random real-valued genome within uniform bounds.

        Args:
            length: Number of genes.
            lower: Lower bound for each gene.
            upper: Upper bound for each gene.

        Returns:
            A new RealValuedGenome with uniform random values.
        """
        return cls(
            values=[random.uniform(lower, upper) for _ in range(length)],
            lower_bounds=[lower] * length,
            upper_bounds=[upper] * length,
        )

    def copy(self) -> RealValuedGenome:
        """Execute Copy operations natively."""
        return RealValuedGenome(
            values=list(self.values),
            lower_bounds=list(self.lower_bounds) if self.lower_bounds else None,
            upper_bounds=list(self.upper_bounds) if self.upper_bounds else None,
        )

    def to_list(self) -> list[float]:
        """Execute To List operations natively."""
        return list(self.values)

    def __len__(self) -> int:
        """Execute   Len   operations natively."""
        return len(self.values)

    def clip(self) -> None:
        """Clamp every gene to its bounds (in-place)."""
        for i in range(len(self.values)):
            lo = self.lower_bounds[i] if self.lower_bounds else float("-inf")
            hi = self.upper_bounds[i] if self.upper_bounds else float("inf")
            self.values[i] = max(lo, min(hi, self.values[i]))


@dataclass
class PermutationGenome(Genome):
    """Permutation genome — an ordered arrangement of unique elements.

    Useful for problems like the travelling salesman, job scheduling, or
    any ordering/sequencing optimisation.

    Attributes:
        elements: The ordered sequence of unique elements.
    """
    elements: list[Any] = field(default_factory=list)

    @classmethod
    def random(cls, n: int) -> PermutationGenome:
        """Create a random permutation of integers [0, n).

        Args:
            n: Number of elements.

        Returns:
            A new PermutationGenome with a random ordering.
        """
        elems = list(range(n))
        random.shuffle(elems)
        return cls(elements=elems)

    @classmethod
    def from_elements(cls, elements: list[Any]) -> PermutationGenome:
        """Create a permutation genome from a pre-ordered element list.

        Args:
            elements: The elements in their initial order.

        Returns:
            A new PermutationGenome.
        """
        return cls(elements=list(elements))

    def copy(self) -> PermutationGenome:
        """Execute Copy operations natively."""
        return PermutationGenome(elements=copy.deepcopy(self.elements))

    def to_list(self) -> list[Any]:
        """Execute To List operations natively."""
        return list(self.elements)

    def __len__(self) -> int:
        """Execute   Len   operations natively."""
        return len(self.elements)

    def swap(self, i: int, j: int) -> None:
        """Swap the elements at indices *i* and *j*."""
        self.elements[i], self.elements[j] = self.elements[j], self.elements[i]


__all__ = [
    "BinaryGenome",
    "Genome",
    "PermutationGenome",
    "RealValuedGenome",
]
