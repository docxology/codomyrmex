"""
Multi-agent coordination submodule.

Agent definitions and lifecycle management for collaborative workflows.
"""

from .base import AbstractAgent, CollaborativeAgent
from .worker import WorkerAgent, SpecializedWorker
from .supervisor import SupervisorAgent
from .registry import AgentRegistry, get_registry

__all__ = [
    # Base classes
    "AbstractAgent",
    "CollaborativeAgent",
    # Worker agents
    "WorkerAgent",
    "SpecializedWorker",
    # Supervisor
    "SupervisorAgent",
    # Registry
    "AgentRegistry",
    "get_registry",
]
