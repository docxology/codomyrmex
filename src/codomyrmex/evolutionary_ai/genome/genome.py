"""Genome and Gene definitions."""

import random


class Genome:
    """Represents an individual's genetic information."""

    def __init__(self, genes: list[float]):
        self.genes = genes
        self.fitness: float | None = None

    @classmethod
    def random(cls, length: int):
        """Create a random genome of given length."""
        return cls([random.random() for _ in range(length)])

    def __len__(self):
        return len(self.genes)

    def __repr__(self):
        return f"Genome(fitness={self.fitness}, length={len(self)})"
