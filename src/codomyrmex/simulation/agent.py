"""Abstract base class for simulation agents.

This module defines the interface for agents that interact with the simulation environment.
"""

import abc
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Action:
    """Represents an action taken by an agent."""
    type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


class Agent(abc.ABC):
    """Abstract base class for all simulation agents."""

    def __init__(self, agent_id: str, name: str = ""):
        """Initialize the agent.

        Args:
            agent_id: Unique identifier for the agent.
            name: Human-readable name for the agent.
        """
        self.id = agent_id
        self.name = name or agent_id
        self.step_count = 0
        self._history: List[Action] = []

    @abc.abstractmethod
    def act(self, observation: Dict[str, Any]) -> Action:
        """Decide on an action given the current observation.

        Args:
            observation: The current state of the environment as perceived by the agent.

        Returns:
            The action the agent has decided to take.
        """
        pass

    def learn(self, reward: float) -> None:
        """Update internal state based on the reward received.

        Args:
            reward: The reward signal from the environment.
        """
        # Default implementation does nothing; override in learning agents
        pass

    def reset(self) -> None:
        """Reset the agent to its initial state."""
        self.step_count = 0
        self._history.clear()

    def record_action(self, action: Action) -> None:
        """Record an action in the agent's history.

        Args:
            action: The action to record.
        """
        self._history.append(action)
        self.step_count += 1
