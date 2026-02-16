"""Ant Colony simulation subpackage.

Provides ant agents, colony management, and environment simulation
using pheromone-based foraging algorithms.
"""

from .ant import Ant, AntState
from .colony import Colony
from .environment import Environment

__all__ = ["Ant", "AntState", "Colony", "Environment"]
