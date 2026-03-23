"""Ant agent for colony simulation.

Each ant is an autonomous agent that forages for food, deposits pheromone
trails, and returns food to the colony nest.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codomyrmex.bio_simulation.genomics.genome import Genome


class AntState(Enum):
    """Possible behavioral states for an ant."""

    FORAGING = auto()
    RETURNING = auto()
    RESTING = auto()
    IDLE = auto()


@dataclass
class Ant:
    """A single ant agent in the colony simulation.

    Attributes:
        id: Unique identifier for the ant.
        position: Current (x, y) coordinates on the environment grid.
        state: Current behavioral state (FORAGING, RETURNING, RESTING, IDLE).
        energy: Remaining energy level [0.0, 1.0].
        carrying: Whether carrying food.
        genome: Genetic profile of the ant.
        age_ticks: Ticks since spawning.
        pheromone_trail: Ordered list of positions visited since last state change.
    """

    id: int
    position: tuple[float, float] = (0.0, 0.0)
    state: AntState = AntState.IDLE
    energy: float = 1.0
    carrying: bool = False
    genome: Genome | None = None
    age_ticks: int = 0
    pheromone_trail: list[tuple[float, float]] = field(default_factory=list)

    # Internal movement speed (cells per step)
    _speed: float = field(default=1.0, repr=False)
    _carried_amount: float = field(default=0.0, repr=False)

    def move(self, direction: tuple[float, float]) -> None:
        """Move the ant in the given direction vector.

        The direction is normalized and scaled by the ant's speed. Moving
        costs energy proportional to the distance traveled.

        Args:
            direction: (dx, dy) direction vector. Need not be unit length.
        """
        if not self.is_alive():
            return

        dx, dy = direction
        magnitude = math.hypot(dx, dy)
        if magnitude == 0:
            return

        # Normalize and scale
        speed = self._speed
        if self.genome and "speed" in self.genome.traits:
            speed *= 0.5 + self.genome.traits["speed"]

        nx = (dx / magnitude) * speed
        ny = (dy / magnitude) * speed

        old_x, old_y = self.position
        self.position = (old_x + nx, old_y + ny)

        # Record trail for pheromone deposit
        self.pheromone_trail.append(self.position)

        # Energy cost proportional to distance
        cost = speed * 0.005
        if self.genome and "endurance" in self.genome.traits:
            cost *= 1.5 - self.genome.traits["endurance"]

        self.energy = max(0.0, self.energy - cost)
        self.age_ticks += 1

    def deposit_pheromone(self, strength: float) -> list[tuple[tuple[int, int], float]]:
        """Generate pheromone deposits along the recorded trail.

        Returns a list of (position, amount) tuples that the environment
        should apply to the pheromone map. Strength decays linearly from
        the most recent position backward along the trail.

        Args:
            strength: Base pheromone strength at the most recent position.

        Returns:
            list of (position, amount) pairs.
        """
        deposits: list[tuple[tuple[int, int], float]] = []
        trail_len = len(self.pheromone_trail)
        if trail_len == 0:
            return deposits

        for idx, pos in enumerate(reversed(self.pheromone_trail)):
            decay = strength * (1.0 - idx / max(trail_len, 1))
            if decay > 0:
                grid_pos = (round(pos[0]), round(pos[1]))
                deposits.append((grid_pos, decay))

        return deposits

    def pick_up_food(self, amount: float) -> float:
        """Pick up food, limited by a maximum carry capacity.

        Args:
            amount: Amount of food available at the current location.

        Returns:
            The actual amount picked up.
        """
        if self.carrying:
            return 0.0

        max_carry = 10.0
        if self.genome and "strength" in self.genome.traits:
            max_carry *= 0.5 + self.genome.traits["strength"]

        picked = min(amount, max_carry)
        if picked > 0:
            self._carried_amount = picked
            self.carrying = True
            self.state = AntState.RETURNING
            self.pheromone_trail = [self.position]
        return picked

    def drop_food(self) -> float:
        """Drop all carried food (at the nest). Returns amount dropped."""
        if not self.is_alive():
            return 0.0

        dropped = self._carried_amount
        self._carried_amount = 0.0
        self.carrying = False
        self.state = AntState.RESTING
        self.pheromone_trail = [self.position]
        return dropped

    def is_alive(self) -> bool:
        """Check whether the ant still has energy to act."""
        return self.energy > 0

    def distance_to(self, target: tuple[float, float]) -> float:
        """Euclidean distance from current position to a target."""
        return math.hypot(target[0] - self.position[0], target[1] - self.position[1])

    @property
    def valid_transitions(self) -> list[AntState]:
        """Returns valid state transitions for the current state."""
        transitions = {
            AntState.FORAGING: [AntState.RETURNING],
            AntState.RETURNING: [AntState.RESTING],
            AntState.RESTING: [AntState.FORAGING, AntState.IDLE],
            AntState.IDLE: [AntState.FORAGING],
        }
        return transitions.get(self.state, [])
