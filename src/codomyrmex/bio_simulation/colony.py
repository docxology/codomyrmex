from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List
from random import choice

class AntState(Enum):
    FORAGING = auto()
    RETURNING = auto()
    DEFENDING = auto()
    IDLE = auto()

@dataclass
class Ant:
    """Simulated biological agent."""
    id: int
    state: AntState = AntState.IDLE
    energy: float = 100.0
    x: int = 0
    y: int = 0

    def step(self):
        """Perform one simulation step."""
        self.energy -= 0.1
        if self.state == AntState.FORAGING:
            self.x += choice([-1, 0, 1])
            self.y += choice([-1, 0, 1])

class Colony:
    """Ant colony simulation environment."""
    
    def __init__(self, population_size: int):
        self.ants = [Ant(id=i) for i in range(population_size)]
        self.tick = 0

    def step(self):
        """Advance simulation by one tick."""
        self.tick += 1
        for ant in self.ants:
            if ant.energy > 0:
                ant.step()

    def get_census(self) -> dict:
        """Count ants by state."""
        counts = {state: 0 for state in AntState}
        for ant in self.ants:
            counts[ant.state] += 1
        return counts
