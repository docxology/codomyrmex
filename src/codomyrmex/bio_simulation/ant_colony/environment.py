"""Grid-based environment for the ant colony simulation.

The environment maintains a 2-D grid that tracks pheromone levels,
food sources, and obstacles. Coordinates are integer grid cells.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class FoodSource:
    """A localized food deposit in the environment."""

    position: tuple[int, int]
    amount: float


class Environment:
    """Grid-based environment for ant colony simulation.

    The grid stores pheromone intensity per cell. Food sources and
    obstacles are tracked separately.

    Attributes:
        width: Number of columns in the grid.
        height: Number of rows in the grid.
        nest_position: Location of the colony nest.
        pheromone_decay: Decay rate per tick [0.0, 1.0].
    """

    def __init__(
        self,
        width: int = 100,
        height: int = 100,
        nest_position: tuple[int, int] | None = None,
        food_sources: int = 10,
        pheromone_decay: float = 0.05,
    ) -> None:
        """Initialize the environment grid.

        Args:
            width: Grid width in cells.
            height: Grid height in cells.
            nest_position: (x, y) of the colony nest. Defaults to center.
            food_sources: Initial number of random food sources.
            pheromone_decay: Decay rate per tick.
        """
        self.width = width
        self.height = height
        self.nest_position = nest_position or (width // 2, height // 2)
        self.pheromone_decay = pheromone_decay

        # Pheromone map: keyed by (x, y) -> intensity
        self._pheromones: dict[tuple[int, int], float] = {}

        # Food sources
        self._food_sources: list[FoodSource] = []

        # Add random food sources if requested (simulated for now, usually done by Colony)
        # In a real impl, we might use a seed here too.

        # Obstacle set
        self._obstacles: set[tuple[int, int]] = set()

    def add_food_source(self, position: tuple[int, int], amount: float) -> None:
        """Place a food source at the given grid position.

        Args:
            position: (x, y) grid cell.
            amount: Quantity of food available.
        """
        # Merge with existing source at same position if present
        for fs in self._food_sources:
            if fs.position == position:
                fs.amount += amount
                return
        self._food_sources.append(FoodSource(position=position, amount=amount))

    def remove_food(self, position: tuple[int, int], amount: float) -> float:
        """Remove food from a source, returning the actual amount removed."""
        for fs in self._food_sources:
            if fs.position == position:
                taken = min(fs.amount, amount)
                fs.amount -= taken
                if fs.amount <= 0:
                    self._food_sources.remove(fs)
                return taken
        return 0.0

    def add_obstacle(self, position: tuple[int, int]) -> None:
        """Mark a grid cell as impassable.

        Args:
            position: (x, y) grid cell to block.
        """
        self._obstacles.add(position)

    def is_passable(self, position: tuple[int, int]) -> bool:
        """Check whether a grid cell is passable (not an obstacle and in-bounds)."""
        x, y = position
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return position not in self._obstacles

    def get_pheromone_map(self) -> dict[tuple[int, int], float]:
        """Return a copy of the current pheromone intensity map.

        Returns:
            Dictionary mapping (x, y) to pheromone intensity.
        """
        return dict(self._pheromones)

    def set_pheromone(self, position: tuple[int, int], amount: float) -> None:
        """Set pheromone intensity at a specific cell."""
        ix, iy = round(position[0]), round(position[1])
        if 0 <= ix < self.width and 0 <= iy < self.height:
            self._pheromones[(ix, iy)] = self._pheromones.get((ix, iy), 0.0) + amount

    def decay_pheromones(self, rate: float | None = None) -> None:
        """Reduce all pheromone intensities by a multiplicative decay factor.

        After decay, cells that fall below a threshold (0.01) are removed
        to keep the map sparse.

        Args:
            rate: Decay multiplier in (0, 1). Defaults to (1 - self.pheromone_decay).
        """
        decay_rate = 1.0 - self.pheromone_decay if rate is None else rate

        to_remove: list[tuple[int, int]] = []
        for pos in self._pheromones:
            self._pheromones[pos] *= decay_rate
            if self._pheromones[pos] < 0.01:
                to_remove.append(pos)
        for pos in to_remove:
            del self._pheromones[pos]

    def get_neighbors(
        self, position: tuple[int, int], radius: int = 1
    ) -> list[tuple[int, int]]:
        """Return passable neighboring cells within a Chebyshev radius.

        Args:
            position: Center cell.
            radius: Maximum Chebyshev distance (default 1 = 8-connected).

        Returns:
            List of passable (x, y) cells within the radius.
        """
        cx, cy = position
        neighbors: list[tuple[int, int]] = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cx + dx, cy + dy
                if self.is_passable((nx, ny)):
                    neighbors.append((nx, ny))
        return neighbors

    def food_at(
        self, position: tuple[int, int], radius: float = 1.5
    ) -> FoodSource | None:
        """Find the nearest food source within the given radius of a position."""
        best: FoodSource | None = None
        best_dist = float("inf")
        for fs in self._food_sources:
            dist = math.hypot(
                fs.position[0] - position[0], fs.position[1] - position[1]
            )
            if dist <= radius and dist < best_dist:
                best = fs
                best_dist = dist
        return best

    @property
    def food_sources(self) -> list[FoodSource]:
        """Read-only access to current food sources."""
        return list(self._food_sources)

    @property
    def obstacles(self) -> set[tuple[int, int]]:
        """Read-only access to obstacle positions."""
        return set(self._obstacles)
