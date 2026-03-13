"""Metabolic Bioreactor Simulation.

Models continuous timestep deterministic chemical reactions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass(slots=True)
class Metabolite:
    """A chemical or biological substance with a current concentration."""

    name: str
    concentration: float
    degradation_rate: float = 0.0


@dataclass(slots=True)
class Reaction:
    """A reaction transforming substrates into products at a specific rate."""

    substrates: list[str]
    products: list[str]
    # Function taking dict of all current concentrations and returning the reaction velocity
    velocity_fn: Callable[[dict[str, float]], float]


@dataclass
class BioReactor:
    """Simulates the metabolic state over time via deterministic differencing."""

    metabolites: dict[str, Metabolite] = field(default_factory=dict)
    reactions: list[Reaction] = field(default_factory=list)
    time: float = 0.0

    def add_metabolite(
        self, name: str, initial_concentration: float, degradation_rate: float = 0.0
    ) -> None:
        """Add a trackable metabolite to the reactor."""
        self.metabolites[name] = Metabolite(
            name=name,
            concentration=max(0.0, initial_concentration),
            degradation_rate=degradation_rate,
        )

    def add_reaction(self, reaction: Reaction) -> None:
        """Add a metabolic reaction pathway."""
        self.reactions.append(reaction)

    def step(self, dt: float = 0.1) -> None:
        """Advance the simulation by dt time units using Euler integration."""
        if dt <= 0:
            return

        # Snap read state
        concs = {name: meta.concentration for name, meta in self.metabolites.items()}

        # Calculate deltas
        deltas = {
            name: -meta.degradation_rate * meta.concentration * dt
            for name, meta in self.metabolites.items()
        }

        for rx in self.reactions:
            v = rx.velocity_fn(concs)
            # Ensure velocity doesn't drive substrates below 0
            max_v = float("inf")
            for sub in rx.substrates:
                if concs[sub] <= 0:
                    max_v = 0.0
                    break
                # Approx constraint
                safe_v = concs[sub] / dt
                max_v = min(max_v, safe_v)

            v = max(0.0, min(v, max_v))

            # Apply deltas
            for sub in rx.substrates:
                deltas[sub] -= v * dt
            for prod in rx.products:
                deltas[prod] += v * dt

        # Commit state
        for name, meta in self.metabolites.items():
            meta.concentration = max(0.0, meta.concentration + deltas[name])

        self.time += dt

    def run(self, steps: int = 100, dt: float = 0.1) -> dict[str, list[float]]:
        """Run the simulation for multiple steps, recording history.

        Returns:
            Dictionary mapped by metabolite name to a list of its concentrations over time.
        """
        history: dict[str, list[float]] = {
            name: [m.concentration] for name, m in self.metabolites.items()
        }
        for _ in range(steps):
            self.step(dt)
            for name, meta in self.metabolites.items():
                history[name].append(meta.concentration)
        return history
