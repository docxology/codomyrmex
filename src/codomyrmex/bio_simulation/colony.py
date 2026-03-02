"""Ant colony simulation — Ant agents and Colony orchestrator.

Provides:
- AntState: Behavioral state enum (FORAGING, RETURNING, DEFENDING, IDLE, SCOUTING)
- Ant: Simulated biological agent with energy, pheromone, and carrying capacity
- Colony: Multi-ant simulation with pheromone grid, food sources, and statistics
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class AntState(Enum):
    """Functional component: AntState."""
    FORAGING = auto()
    RETURNING = auto()
    DEFENDING = auto()
    IDLE = auto()
    SCOUTING = auto()


@dataclass
class Ant:
    """Simulated biological agent with energy, position, and carrying capacity."""

    id: int
    state: AntState = AntState.IDLE
    energy: float = 100.0
    x: int = 0
    y: int = 0
    carrying: float = 0.0  # food units being carried
    max_carry: float = 1.0
    speed: int = 1
    age: int = 0

    def step(self) -> None:
        """Perform one simulation step."""
        self.energy -= 0.1
        self.age += 1

        if self.state == AntState.FORAGING:
            self._move_random()
        elif self.state == AntState.RETURNING:
            self._move_toward(0, 0)  # return to nest at origin
        elif self.state == AntState.SCOUTING:
            self._move_random()
            self._move_random()  # scouts move faster
        elif self.state == AntState.DEFENDING:
            pass  # hold position

    def _move_random(self) -> None:
        self.x += random.choice([-self.speed, 0, self.speed])
        self.y += random.choice([-self.speed, 0, self.speed])

    def _move_toward(self, tx: int, ty: int) -> None:
        """Move one step toward target."""
        if self.x < tx:
            self.x += self.speed
        elif self.x > tx:
            self.x -= self.speed
        if self.y < ty:
            self.y += self.speed
        elif self.y > ty:
            self.y -= self.speed

    def pick_up_food(self, available: float) -> float:
        """Pick up food, limited by carrying capacity. Returns amount taken."""
        can_carry = self.max_carry - self.carrying
        taken = min(can_carry, available)
        self.carrying += taken
        if taken > 0:
            self.state = AntState.RETURNING
        return taken

    def drop_food(self) -> float:
        """Drop all carried food. Returns amount dropped."""
        dropped = self.carrying
        self.carrying = 0.0
        self.state = AntState.IDLE
        return dropped

    @property
    def is_alive(self) -> bool:
        return self.energy > 0

    @property
    def distance_from_nest(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "id": self.id, "state": self.state.name, "energy": self.energy,
            "x": self.x, "y": self.y, "carrying": self.carrying, "age": self.age,
        }


@dataclass
class FoodSource:
    """A food source in the environment."""

    x: int
    y: int
    amount: float
    radius: float = 2.0


class Colony:
    """Ant colony simulation with food sources, pheromones, and statistics.

    Example::

        colony = Colony(population_size=50)
        colony.add_food(10, 10, amount=100)
        for _ in range(100):
            colony.step()
        print(colony.stats())
    """

    def __init__(self, population_size: int, grid_size: int = 100) -> None:
        self.ants = [Ant(id=i) for i in range(population_size)]
        self.tick = 0
        self.grid_size = grid_size
        self._food_sources: list[FoodSource] = []
        self._food_collected: float = 0.0
        self._pheromone_grid: dict[tuple[int, int], float] = defaultdict(float)

    def add_food(self, x: int, y: int, amount: float, radius: float = 2.0) -> None:
        """Add a food source to the environment."""
        self._food_sources.append(FoodSource(x=x, y=y, amount=amount, radius=radius))

    def step(self) -> None:
        """Advance simulation by one tick."""
        self.tick += 1
        for ant in self.ants:
            if not ant.is_alive:
                continue
            ant.step()
            self._check_food(ant)
            self._check_nest(ant)
            # Deposit pheromone if returning with food
            if ant.state == AntState.RETURNING and ant.carrying > 0:
                self._pheromone_grid[(ant.x, ant.y)] += 0.5
        self._decay_pheromones()

    def _check_food(self, ant: Ant) -> None:
        """Check if ant is near a food source and can pick up food."""
        if ant.state not in (AntState.FORAGING, AntState.SCOUTING):
            return
        for source in self._food_sources:
            if source.amount <= 0:
                continue
            dist = math.sqrt((ant.x - source.x) ** 2 + (ant.y - source.y) ** 2)
            if dist <= source.radius:
                taken = ant.pick_up_food(source.amount)
                source.amount -= taken

    def _check_nest(self, ant: Ant) -> None:
        """Check if returning ant has reached the nest."""
        if ant.state == AntState.RETURNING and ant.distance_from_nest < 2:
            self._food_collected += ant.drop_food()

    def _decay_pheromones(self, rate: float = 0.95) -> None:
        """Decay all pheromone levels."""
        to_remove = []
        for key in self._pheromone_grid:
            self._pheromone_grid[key] *= rate
            if self._pheromone_grid[key] < 0.01:
                to_remove.append(key)
        for key in to_remove:
            del self._pheromone_grid[key]

    def get_census(self) -> dict[AntState, int]:
        """Count ants by state."""
        counts: dict[AntState, int] = dict.fromkeys(AntState, 0)
        for ant in self.ants:
            if ant.is_alive:
                counts[ant.state] += 1
        return counts

    def set_foraging(self, count: int) -> None:
        """Set N idle ants to foraging state."""
        set_count = 0
        for ant in self.ants:
            if ant.state == AntState.IDLE and ant.is_alive and set_count < count:
                ant.state = AntState.FORAGING
                set_count += 1

    def stats(self) -> dict[str, Any]:
        """Return simulation statistics."""
        alive = [a for a in self.ants if a.is_alive]
        return {
            "tick": self.tick,
            "alive": len(alive),
            "dead": len(self.ants) - len(alive),
            "food_collected": self._food_collected,
            "food_remaining": sum(s.amount for s in self._food_sources),
            "census": self.get_census(),
            "avg_energy": sum(a.energy for a in alive) / max(len(alive), 1),
            "pheromone_cells": len(self._pheromone_grid),
        }

    @property
    def food_collected(self) -> float:
        return self._food_collected

    @property
    def population_alive(self) -> int:
        return sum(1 for a in self.ants if a.is_alive)
