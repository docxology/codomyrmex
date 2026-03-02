"""Data models for the memetics submodule."""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MemeType(StrEnum):
    """Classification of meme types by cognitive function."""

    BELIEF = "belief"
    NORM = "norm"
    STRATEGY = "strategy"
    AESTHETIC = "aesthetic"
    NARRATIVE = "narrative"
    SYMBOL = "symbol"
    RITUAL = "ritual"
    SLOGAN = "slogan"


@dataclass
class Meme:
    """A discrete replicable information unit.

    Attributes:
        content: Textual representation of the meme.
        meme_type: Functional classification.
        fidelity: Copy-fidelity score (0–1). Higher means it resists mutation.
        fecundity: Replication rate (0–1). Higher means more copies per unit time.
        longevity: Persistence score (0–1). Higher means longer survival.
        lineage: Ordered list of ancestor meme IDs (mutation history).
        metadata: Arbitrary key-value metadata.
        id: Unique identifier, auto-generated from content hash + timestamp.
        created_at: Unix timestamp of creation.
    """

    content: str
    meme_type: MemeType = MemeType.BELIEF
    fidelity: float = 0.8
    fecundity: float = 0.5
    longevity: float = 0.5
    lineage: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default="")
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.id:
            hash_input = f"{self.content}:{self.created_at}:{uuid.uuid4().hex[:8]}"
            self.id = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        # Clamp scores to [0, 1]
        self.fidelity = max(0.0, min(1.0, self.fidelity))
        self.fecundity = max(0.0, min(1.0, self.fecundity))
        self.longevity = max(0.0, min(1.0, self.longevity))

    @property
    def fitness(self) -> float:
        """Composite fitness = geometric mean of fidelity, fecundity, longevity."""
        return (self.fidelity * self.fecundity * self.longevity) ** (1 / 3)

    def descend(self, new_content: str, **overrides: Any) -> Meme:
        """Create a mutated descendant, preserving lineage."""
        child_lineage = self.lineage + [self.id]
        return Meme(
            content=new_content,
            meme_type=overrides.get("meme_type", self.meme_type),
            fidelity=overrides.get("fidelity", self.fidelity),
            fecundity=overrides.get("fecundity", self.fecundity),
            longevity=overrides.get("longevity", self.longevity),
            lineage=child_lineage,
            metadata={**self.metadata, **overrides.get("metadata", {})},
        )


@dataclass
class MemeticCode:
    """A sequence of memes encoding a coherent information program.

    Like genetic code, memetic code is ordered and functional —
    the sequence matters for the phenotypic expression of the idea.
    """

    sequence: list[Meme] = field(default_factory=list)

    def append(self, meme: Meme) -> None:
        """Append a meme to the code sequence."""
        self.sequence.append(meme)

    def splice_in(self, index: int, meme: Meme) -> None:
        """Insert a meme at a specific position in the sequence."""
        self.sequence.insert(index, meme)

    def excise(self, index: int) -> Meme:
        """Remove and return the meme at a specific position."""
        return self.sequence.pop(index)

    @property
    def length(self) -> int:
        """length ."""
        return len(self.sequence)

    @property
    def aggregate_fitness(self) -> float:
        """Mean fitness across all memes in the code."""
        if not self.sequence:
            return 0.0
        return sum(m.fitness for m in self.sequence) / len(self.sequence)


@dataclass
class Memeplex:
    """A co-adapted complex of memes that replicate together.

    A memeplex is more than the sum of its parts — memes within a
    memeplex reinforce each other's survival and replication.

    Attributes:
        name: Human-readable identifier.
        memes: The constituent memes.
        synergy: How much the memes reinforce each other (0–1).
        id: Unique identifier.
    """

    name: str
    memes: list[Meme] = field(default_factory=list)
    synergy: float = 0.5
    id: str = field(default="")

    def __post_init__(self) -> None:
        if not self.id:
            self.id = hashlib.sha256(
                f"{self.name}:{uuid.uuid4().hex[:8]}".encode()
            ).hexdigest()[:16]
        self.synergy = max(0.0, min(1.0, self.synergy))

    @property
    def fitness(self) -> float:
        """Memeplex fitness = mean meme fitness * synergy bonus."""
        if not self.memes:
            return 0.0
        base = sum(m.fitness for m in self.memes) / len(self.memes)
        return base * (1.0 + self.synergy)

    def robustness_score(self) -> float:
        """How robust is this memeplex to losing individual memes?

        Uses the Gini coefficient of individual meme fitnesses.
        A highly uniform memeplex is more robust.
        """
        if len(self.memes) < 2:
            return 1.0
        fitnesses = sorted(m.fitness for m in self.memes)
        n = len(fitnesses)
        numerator = sum(
            abs(fitnesses[i] - fitnesses[j])
            for i in range(n)
            for j in range(n)
        )
        denominator = 2 * n * sum(fitnesses)
        if denominator == 0:
            return 0.0
        gini = numerator / denominator
        return 1.0 - gini  # Invert: 1 = perfectly uniform = most robust

    def mutate(self, mutation_rate: float = 0.1) -> Memeplex:
        """Create a mutated copy of this memeplex."""
        import random

        new_memes = []
        for meme in self.memes:
            if random.random() < mutation_rate:
                # Slight content perturbation marker
                mutated = meme.descend(
                    new_content=f"{meme.content} [mutated]",
                    fidelity=max(0.0, meme.fidelity + random.gauss(0, 0.05)),
                    fecundity=max(0.0, meme.fecundity + random.gauss(0, 0.05)),
                )
                new_memes.append(mutated)
            else:
                new_memes.append(meme)
        return Memeplex(
            name=f"{self.name}_mutant",
            memes=new_memes,
            synergy=max(0.0, min(1.0, self.synergy + random.gauss(0, 0.02))),
        )

    def recombine(self, other: Memeplex) -> Memeplex:
        """Sexual recombination — crossover at random point."""
        import random

        if not self.memes or not other.memes:
            return Memeplex(name=f"{self.name}x{other.name}", memes=[])
        cut_a = random.randint(0, len(self.memes))
        cut_b = random.randint(0, len(other.memes))
        child_memes = self.memes[:cut_a] + other.memes[cut_b:]
        return Memeplex(
            name=f"{self.name}x{other.name}",
            memes=child_memes,
            synergy=(self.synergy + other.synergy) / 2,
        )


@dataclass
class FitnessMap:
    """A mapping from meme/memeplex IDs to their fitness values.

    Represents a snapshot of the fitness landscape for a population.
    """

    entries: dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def add(self, entity_id: str, fitness: float) -> None:
        """add ."""
        self.entries[entity_id] = fitness

    @property
    def mean_fitness(self) -> float:
        if not self.entries:
            return 0.0
        return sum(self.entries.values()) / len(self.entries)

    @property
    def max_fitness(self) -> float:
        if not self.entries:
            return 0.0
        return max(self.entries.values())

    @property
    def min_fitness(self) -> float:
        if not self.entries:
            return 0.0
        return min(self.entries.values())

    def top_n(self, n: int = 10) -> list[tuple[str, float]]:
        """Return top-N entities by fitness."""
        return sorted(self.entries.items(), key=lambda x: x[1], reverse=True)[:n]
