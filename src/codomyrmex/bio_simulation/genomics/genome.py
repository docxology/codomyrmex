"""Genetic representation for bio simulation.

Provides a Genome class for individual genetic representation and a
Population class that manages selection, crossover, and mutation
across generations.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class Genome:
    """Genetic representation for bio simulation.

    A genome is a fixed-length vector of floating-point gene values in
    the range [0, 1]. Fitness is computed as the sum of all gene
    values (higher is better).

    Attributes:
        traits: Dict of trait names and values, each in [0.0, 1.0].
    """

    traits: dict[str, float] = field(default_factory=dict)

    @classmethod
    def random(cls) -> Genome:
        """Create a genome with random gene values.

        Standard traits: "speed", "strength", "perception", "endurance"

        Returns:
            A new Genome with uniform-random gene values in [0, 1].
        """
        traits = {
            "speed": random.random(),
            "strength": random.random(),
            "perception": random.random(),
            "endurance": random.random(),
        }
        return cls(traits=traits)

    def mutate(self, rate: float) -> Genome:
        """Return a mutated copy of this genome.

        Each trait has an independent probability *rate* of being replaced
        by a new random value drawn from a Gaussian perturbation (clamped
        to [0, 1]).

        Args:
            rate: Per-trait mutation probability in [0, 1].

        Returns:
            A new Genome with mutations applied.
        """
        new_traits: dict[str, float] = {}
        for trait, value in self.traits.items():
            if random.random() < rate:
                mutated = value + random.gauss(0, 0.1)
                mutated = max(0.0, min(1.0, mutated))
                new_traits[trait] = mutated
            else:
                new_traits[trait] = value
        return Genome(traits=new_traits)

    def crossover(self, other: Genome) -> tuple[Genome, Genome]:
        """Simple point crossover with another genome based on traits.

        Args:
            other: The second parent genome.

        Returns:
            A tuple of two offspring Genomes.
        """
        child1_traits = {}
        child2_traits = {}
        
        all_traits = list(set(self.traits.keys()) | set(other.traits.keys()))
        if not all_traits:
            return Genome(), Genome()
            
        point = random.randint(0, len(all_traits))
        
        for i, trait in enumerate(all_traits):
            if i < point:
                child1_traits[trait] = self.traits.get(trait, 0.5)
                child2_traits[trait] = other.traits.get(trait, 0.5)
            else:
                child1_traits[trait] = other.traits.get(trait, 0.5)
                child2_traits[trait] = self.traits.get(trait, 0.5)
                
        return Genome(traits=child1_traits), Genome(traits=child2_traits)

    def fitness_score(self) -> float:
        """Compute a fitness score for this genome.

        The default fitness function returns the mean trait value,
        yielding a score in [0, 1]. Higher is better.

        Returns:
            Fitness value as a float.
        """
        if not self.traits:
            return 0.0
        return sum(self.traits.values()) / len(self.traits)

    def __repr__(self) -> str:
        """Return string representation."""
        trait_str = ", ".join(f"{k}={v:.3f}" for k, v in self.traits.items())
        return f"Genome(fitness={self.fitness_score():.4f}, traits={{{trait_str}}})"
