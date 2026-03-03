"""Ant colony simulation with pheromone-based foraging.

Orchestrates a population of Ant agents within an Environment,
running discrete time-steps of foraging, pheromone signaling, and
food collection.
"""

from __future__ import annotations

import random
from typing import Any

from src.codomyrmex.bio_simulation.genomics.genome import Genome

from .ant import Ant, AntState
from .environment import Environment


class Colony:
    """Ant colony simulation with pheromone-based foraging.

    The colony manages a population of ants, a shared environment, and
    a central nest where food is accumulated.

    Attributes:
        population: Current number of living ants.
        environment: The grid environment the colony inhabits.
        food_collected: Total food returned to the nest so far.
        tick: Current simulation step.
    """

    def __init__(
        self,
        population: int,
        seed: int | None = None,
        environment: dict | None = None,
    ) -> None:
        """Create a colony of the given size in the given environment.

        Args:
            population: Initial number of ants to spawn.
            seed: Random seed for reproducibility.
            environment: Optional environment configuration.
        """
        if population < 0:
            raise ValueError("Population must be non-negative")

        if seed is not None:
            random.seed(seed)

        env_config = environment or {}
        self.environment = Environment(
            width=env_config.get("width", 100),
            height=env_config.get("height", 100),
            nest_position=env_config.get("nest_position"),
            pheromone_decay=env_config.get("pheromone_decay", 0.05),
        )

        self.tick: int = 0
        self.food_collected: float = 0.0
        self._total_births: int = 0
        self._total_deaths: int = 0

        # Spawn ants at the nest
        nest = self.environment.nest_position
        self.ants: list[Ant] = [
            Ant(
                id=i,
                position=(float(nest[0]), float(nest[1])),
                state=AntState.FORAGING,
                energy=1.0,
                genome=Genome.random(),
            )
            for i in range(population)
        ]
        self._total_births = population

    def step(self, hours: int = 1) -> dict:
        """Advance simulation by a number of hours.

        Each hour is 60 ticks. Each tick:
        1. Every living ant acts according to its state.
        2. Pheromones are deposited and decayed.
        3. Statistics are gathered.

        Args:
            hours: Number of hours to simulate.

        Returns:
            A summary of the simulation step.
        """
        if hours < 0:
            raise ValueError("Hours must be non-negative")

        ticks = hours * 60
        food_at_start = self.food_collected
        deaths_at_start = self._total_deaths
        births_at_start = self._total_births

        for _ in range(ticks):
            self._step_tick()

        summary = {
            "ticks_elapsed": ticks,
            "food_collected": int(self.food_collected - food_at_start),
            "deaths": self._total_deaths - deaths_at_start,
            "births": self._total_births - births_at_start,
            "population": self.population_alive,
            "state_distribution": self._get_state_distribution(),
        }
        return summary

    def _step_tick(self) -> None:
        """Execute one simulation tick."""
        self.tick += 1

        active_ants = []
        for ant in self.ants:
            if not ant.is_alive():
                # Ant was already dead or just died before this loop.
                # Since we filter self.ants at the end, any ant here
                # that is dead is a NEW death in this tick.
                self._total_deaths += 1
                continue

            if ant.state == AntState.FORAGING:
                self._forage(ant)
            elif ant.state == AntState.RETURNING:
                self._return_to_nest(ant)
            elif ant.state == AntState.RESTING:
                # Rest and regain energy
                recovery = 0.01
                if ant.genome and "endurance" in ant.genome.traits:
                    recovery *= 0.5 + ant.genome.traits["endurance"]
                ant.energy = min(ant.energy + recovery, 1.0)
                if ant.energy >= 0.9:
                    ant.state = AntState.FORAGING
            elif ant.state == AntState.IDLE:
                if random.random() < 0.1:
                    ant.state = AntState.FORAGING

            # Check for death after action
            if not ant.is_alive():
                self._total_deaths += 1
            else:
                active_ants.append(ant)

        # Remove dead ants from the population
        self.ants = active_ants

        # Decay pheromones each tick
        self.environment.decay_pheromones()

    def _forage(self, ant: Ant) -> None:
        """Move a foraging ant toward food, guided by pheromones."""
        pos = (int(round(ant.position[0])), int(round(ant.position[1])))

        # Check for nearby food
        perception_radius = 1.5
        if ant.genome and "perception" in ant.genome.traits:
            perception_radius *= 0.5 + ant.genome.traits["perception"]

        food = self.environment.food_at(pos, radius=perception_radius)
        if food is not None:
            taken = self.environment.remove_food(food.position, 10.0)
            ant.pick_up_food(taken)
            return

        # Decide direction: bias toward pheromone-rich neighbors
        neighbors = self.environment.get_neighbors(pos)
        if not neighbors:
            # Try to move randomly if stuck
            ant.move((random.uniform(-1, 1), random.uniform(-1, 1)))
            return

        pheromone_map = self.environment.get_pheromone_map()
        weights: list[float] = []
        for n in neighbors:
            weights.append(pheromone_map.get(n, 0.0) + 0.1)  # small baseline

        # Weighted random choice
        total = sum(weights)
        probs = [w / total for w in weights]
        chosen = random.choices(neighbors, weights=probs, k=1)[0]

        direction = (chosen[0] - ant.position[0], chosen[1] - ant.position[1])
        ant.move(direction)

    def _return_to_nest(self, ant: Ant) -> None:
        """Move a returning ant toward the nest and deposit pheromones."""
        nest = self.environment.nest_position
        dist = ant.distance_to((float(nest[0]), float(nest[1])))

        if dist < 1.5:
            # At the nest -- drop food
            dropped = ant.drop_food()
            self.food_collected += dropped
            ant.pheromone_trail.clear()
            return

        # Move toward nest
        dx = nest[0] - ant.position[0]
        dy = nest[1] - ant.position[1]
        ant.move((dx, dy))

        # Deposit pheromones along trail
        deposits = ant.deposit_pheromone(strength=1.0)
        for pos, amount in deposits:
            self.environment.set_pheromone(pos, amount)

    def _get_state_distribution(self) -> dict[str, int]:
        dist = {s.name: 0 for s in AntState}
        for ant in self.ants:
            if ant.is_alive():
                dist[ant.state.name] += 1
        return dist

    def stats(self) -> dict[str, Any]:
        """Return current colony statistics."""
        alive = [a for a in self.ants if a.is_alive()]
        avg_energy = sum(a.energy for a in alive) / max(len(alive), 1)

        return {
            "tick": self.tick,
            "alive": len(alive),
            "dead": self._total_deaths,
            "food_collected": round(self.food_collected, 2),
            "food_remaining": round(
                sum(fs.amount for fs in self.environment.food_sources), 2
            ),
            "state_distribution": self._get_state_distribution(),
            "avg_energy": round(avg_energy, 2),
            "pheromone_cells": len(self.environment.get_pheromone_map()),
        }

    def add_food_source(self, position: tuple[int, int], amount: float) -> None:
        """Add a food source to the colony's environment."""
        self.environment.add_food_source(position, amount)

    @property
    def population_alive(self) -> int:
        return sum(1 for a in self.ants if a.is_alive())
