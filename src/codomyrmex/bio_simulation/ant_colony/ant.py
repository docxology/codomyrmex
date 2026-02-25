"""Ant agent for colony simulation.

Each ant is an autonomous agent that forages for food, deposits pheromone
trails, and returns food to the colony nest.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto


class AntState(Enum):
    """Possible behavioral states for an ant."""
    FORAGING = auto()
    RETURNING = auto()
    IDLE = auto()


@dataclass
class Ant:
    """A single ant agent in the colony simulation.

    Attributes:
        position: Current (x, y) coordinates on the environment grid.
        state: Current behavioral state (FORAGING, RETURNING, IDLE).
        energy: Remaining energy; depleted by movement.
        carrying: Amount of food currently being carried.
        pheromone_trail: Ordered list of positions visited since last state change.
    """

    position: tuple[float, float] = (0.0, 0.0)
    state: AntState = AntState.IDLE
    energy: float = 100.0
    carrying: float = 0.0
    pheromone_trail: list[tuple[float, float]] = field(default_factory=list)

    # Internal movement speed (cells per step)
    _speed: float = field(default=1.0, repr=False)

    def move(self, direction: tuple[float, float]) -> None:
        """Move the ant in the given direction vector.

        The direction is normalized and scaled by the ant's speed.  Moving
        costs energy proportional to the distance traveled.

        Args:
            direction: (dx, dy) direction vector. Need not be unit length.
        """
        dx, dy = direction
        magnitude = math.hypot(dx, dy)
        if magnitude == 0:
            return

        # Normalize and scale
        nx = (dx / magnitude) * self._speed
        ny = (dy / magnitude) * self._speed

        old_x, old_y = self.position
        self.position = (old_x + nx, old_y + ny)

        # Record trail for pheromone deposit
        self.pheromone_trail.append(self.position)

        # Energy cost proportional to distance
        self.energy -= self._speed * 0.5

    def deposit_pheromone(self, strength: float) -> list[tuple[tuple[float, float], float]]:
        """Generate pheromone deposits along the recorded trail.

        Returns a list of (position, amount) tuples that the environment
        should apply to the pheromone map.  Strength decays linearly from
        the most recent position backward along the trail.

        Args:
            strength: Base pheromone strength at the most recent position.

        Returns:
            List of (position, amount) pairs.
        """
        deposits: list[tuple[tuple[float, float], float]] = []
        trail_len = len(self.pheromone_trail)
        if trail_len == 0:
            return deposits

        for idx, pos in enumerate(reversed(self.pheromone_trail)):
            decay = strength * (1.0 - idx / max(trail_len, 1))
            if decay > 0:
                deposits.append((pos, decay))

        return deposits

    def pick_up_food(self, amount: float) -> float:
        """Pick up food, limited by a maximum carry capacity of 10 units.

        Args:
            amount: Amount of food available at the current location.

        Returns:
            The actual amount picked up.
        """
        max_carry = 10.0
        can_carry = max_carry - self.carrying
        picked = min(amount, can_carry)
        self.carrying += picked
        if picked > 0:
            self.state = AntState.RETURNING
            self.pheromone_trail = [self.position]
        return picked

    def drop_food(self) -> float:
        """Drop all carried food (at the nest). Returns amount dropped."""
        dropped = self.carrying
        self.carrying = 0.0
        self.state = AntState.FORAGING
        self.pheromone_trail = [self.position]
        return dropped

    def is_alive(self) -> bool:
        """Check whether the ant still has energy to act."""
        return self.energy > 0

    def distance_to(self, target: tuple[float, float]) -> float:
        """Euclidean distance from current position to a target."""
        return math.hypot(target[0] - self.position[0], target[1] - self.position[1])
