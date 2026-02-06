"""
Multi-agent coordination submodule.

Agent definitions and lifecycle management for collaborative workflows.
"""

from .base import AbstractAgent, CollaborativeAgent
from .registry import AgentRegistry, get_registry
from .supervisor import SupervisorAgent
from .worker import SpecializedWorker, WorkerAgent

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
