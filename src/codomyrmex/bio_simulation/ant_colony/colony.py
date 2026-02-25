"""Ant colony simulation with pheromone-based foraging.

Orchestrates a population of Ant agents within an Environment,
running discrete time-steps of foraging, pheromone signaling, and
food collection.
"""

from __future__ import annotations

import random

from .ant import Ant, AntState
from .environment import Environment


class Colony:
    """Ant colony simulation with pheromone-based foraging.

    The colony manages a population of ants, a shared environment, and
    a central nest where food is accumulated.

    Attributes:
        size: Number of ants in the colony.
        environment: The grid environment the colony inhabits.
        food_collected: Total food returned to the nest so far.
        tick: Current simulation step.
    """

    def __init__(self, size: int, environment: Environment) -> None:
        """Create a colony of the given size in the given environment.

        Args:
            size: Number of ants to spawn.
            environment: The Environment instance for the simulation.
        """
        self.size = size
        self.environment = environment
        self.tick: int = 0
        self.food_collected: float = 0.0

        # Spawn ants at the nest
        nest = environment.nest_position
        self.ants: list[Ant] = [
            Ant(
                position=(float(nest[0]), float(nest[1])),
                state=AntState.FORAGING,
                energy=100.0,
            )
            for _ in range(size)
        ]

    def simulate_step(self) -> dict:
        """Execute one simulation tick.

        Each tick:
        1. Every living ant acts according to its state.
        2. Pheromones are deposited and decayed.
        3. Statistics are gathered.

        Returns:
            A dict with keys: tick, alive, food_collected, food_remaining.
        """
        self.tick += 1

        for ant in self.ants:
            if not ant.is_alive():
                continue

            if ant.state == AntState.FORAGING:
                self._forage(ant)
            elif ant.state == AntState.RETURNING:
                self._return_to_nest(ant)
            elif ant.state == AntState.IDLE:
                # Idle ants rest and regain a small amount of energy
                ant.energy = min(ant.energy + 0.5, 100.0)
                if random.random() < 0.1:
                    ant.state = AntState.FORAGING

        # Decay pheromones each tick
        self.environment.decay_pheromones(rate=0.95)

        return {
            "tick": self.tick,
            "alive": sum(1 for a in self.ants if a.is_alive()),
            "food_collected": round(self.food_collected, 2),
            "food_remaining": round(
                sum(fs.amount for fs in self.environment.food_sources), 2
            ),
        }

    def get_stats(self) -> dict:
        """Return current colony statistics.

        Returns:
            Dictionary with population breakdown, food stats, and tick count.
        """
        alive = [a for a in self.ants if a.is_alive()]
        state_counts = {s.name: 0 for s in AntState}
        for ant in alive:
            state_counts[ant.state.name] += 1

        avg_energy = sum(a.energy for a in alive) / max(len(alive), 1)

        return {
            "tick": self.tick,
            "population": len(alive),
            "dead": self.size - len(alive),
            "states": state_counts,
            "average_energy": round(avg_energy, 2),
            "food_collected": round(self.food_collected, 2),
            "food_remaining": round(
                sum(fs.amount for fs in self.environment.food_sources), 2
            ),
            "pheromone_cells": len(self.environment.get_pheromone_map()),
        }

    def add_food_source(self, position: tuple[int, int], amount: float) -> None:
        """Add a food source to the colony's environment.

        Args:
            position: (x, y) grid cell for the food.
            amount: Quantity of food to place.
        """
        self.environment.add_food_source(position, amount)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _forage(self, ant: Ant) -> None:
        """Move a foraging ant toward food, guided by pheromones."""
        pos = (int(round(ant.position[0])), int(round(ant.position[1])))

        # Check for nearby food
        food = self.environment.food_at(pos)
        if food is not None:
            taken = self.environment.remove_food(food.position, min(10.0, food.amount))
            ant.pick_up_food(taken)
            return

        # Decide direction: bias toward pheromone-rich neighbors
        neighbors = self.environment.get_neighbors(pos)
        if not neighbors:
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
            self.environment.set_pheromone(
                (int(round(pos[0])), int(round(pos[1]))), amount
            )
