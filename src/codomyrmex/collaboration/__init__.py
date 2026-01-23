"""Collaboration module for Codomyrmex."""

from .protocols.swarm import SwarmManager, AgentProxy, TaskDecomposer

# Submodule exports
from . import agents
from . import communication
from . import coordination
from . import protocols

__all__ = [
    "SwarmManager",
    "AgentProxy",
    "TaskDecomposer",
    "agents",
    "communication",
    "coordination",
    "protocols",
]

__version__ = "0.1.0"

