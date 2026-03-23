"""Cellular Automaton Model.

Implements Conway's Game of Life and general grid-based cellular behaviors.
"""

from __future__ import annotations


class CellularAutomaton:
    """A 2D cellular grid evolving over discrete generations."""

    def __init__(self, width: int, height: int, default_val: int = 0) -> None:
        self.width = width
        self.height = height
        self.grid: list[list[int]] = [
            [default_val for _ in range(width)] for _ in range(height)
        ]

    def set_cell(self, x: int, y: int, val: int) -> None:
        """set a specific cell (wraps toroidally)."""
        self.grid[y % self.height][x % self.width] = val

    def get_cell(self, x: int, y: int) -> int:
        """Get a specific cell (wraps toroidally)."""
        return self.grid[y % self.height][x % self.width]

    def _count_neighbors(self, x: int, y: int) -> int:
        """Count Moore neighborhood active cells."""
        count = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if self.get_cell(x + dx, y + dy) > 0:
                    count += 1
        return count

    def step(self) -> None:
        """Advance standard Conway's Game of Life rules one generation."""
        new_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

        for y in range(self.height):
            for x in range(self.width):
                state = self.grid[y][x]
                neighbors = self._count_neighbors(x, y)

                if (state == 1 and neighbors in (2, 3)) or (
                    state == 0 and neighbors == 3
                ):
                    new_grid[y][x] = 1
                else:
                    new_grid[y][x] = 0

        self.grid = new_grid

    def render(self) -> str:
        """Render grid to ASCII."""
        rows = []
        for y in range(self.height):
            rows.append("".join("█" if v > 0 else "░" for v in self.grid[y]))
        return "\n".join(rows)

    @classmethod
    def glider(
        cls, offset_x: int = 0, offset_y: int = 0, width: int = 10, height: int = 10
    ) -> CellularAutomaton:
        """Create a grid with a glider at the specified offset."""
        ca = cls(width, height)
        # standard glider shape
        ca.set_cell(offset_x + 1, offset_y, 1)
        ca.set_cell(offset_x + 2, offset_y + 1, 1)
        ca.set_cell(offset_x, offset_y + 2, 1)
        ca.set_cell(offset_x + 1, offset_y + 2, 1)
        ca.set_cell(offset_x + 2, offset_y + 2, 1)
        return ca
