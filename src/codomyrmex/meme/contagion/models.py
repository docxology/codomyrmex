"""Data models for the contagion submodule."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CascadeType(str, Enum):
    """Classification of information cascades."""

    VIRAL = "viral"  # Explosive growth
    ORGANIC = "organic"  # Slower, network-driven growth
    MANUFACTURED = "manufactured"  # Bot-driven/coordinated
    DAMPENED = "dampened"  # Active suppression


@dataclass
class Cascade:
    """A detected information cascade event.

    Attributes:
        seed_id: Originating meme/node ID.
        size: Total nodes reached.
        depth: Maximum path length from seed.
        duration: Time span of the cascade.
        velocity: Average new nodes per time unit.
        cascade_type: Classification.
    """

    seed_id: str
    size: int
    depth: int = 1
    duration: float = 0.0
    velocity: float = 0.0
    cascade_type: CascadeType = CascadeType.ORGANIC
    participants: list[str] = field(default_factory=list)


@dataclass
class PropagationTrace:
    """Detailed log of a single propagation simulation run.

    Attributes:
        time_steps: List of time points.
        infected_counts: Number of infected nodes at each step.
        susceptible_counts: Number of susceptible nodes at each step.
        recovered_counts: Number of recovered nodes at each step.
        seed_meme: The meme being propagated.
    """

    time_steps: list[int] = field(default_factory=list)
    infected_counts: list[int] = field(default_factory=list)
    susceptible_counts: list[int] = field(default_factory=list)
    recovered_counts: list[int] = field(default_factory=list)
    seed_meme_id: str = ""

    def peak_infected(self) -> int:
        """Maximum simultaneous infections."""
        return max(self.infected_counts) if self.infected_counts else 0

    def total_infected(self) -> int:
        """Total distinct infections (approximate from recovered + final infected)."""
        if not self.recovered_counts:
            return 0
        return self.recovered_counts[-1] + self.infected_counts[-1]


@dataclass
class ResonanceMap:
    """Map of network resonance/amplification potential.

    Attributes:
        nodes: Map of node ID to resonance score (0-1).
        clusters: Identified high-resonance clusters.
    """

    nodes: dict[str, float] = field(default_factory=dict)
    clusters: list[list[str]] = field(default_factory=list)


@dataclass
class ContagionModel:
    """Base configuration for a contagion simulation.

    Attributes:
        infection_rate: Probability of transmission per contact (beta).
        recovery_rate: Probability of recovery per step (gamma).
        network_size: Total population size.
    """

    infection_rate: float = 0.3
    recovery_rate: float = 0.1
    network_size: int = 1000
