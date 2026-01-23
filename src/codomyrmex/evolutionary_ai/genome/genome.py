"""Genome and Gene definitions."""

import random
from typing import List, Optional

class Genome:
    """Represents an individual's genetic information."""
    
    def __init__(self, genes: List[float]):
        self.genes = genes
        self.fitness: Optional[float] = None

    @classmethod
    def random(cls, length: int):
        """Create a random genome of given length."""
        return cls([random.random() for _ in range(length)])

    def __len__(self):
        return len(self.genes)

    def __repr__(self):
        return f"Genome(fitness={self.fitness}, length={len(self)})"
