"""Simulation agents — abstract base and concrete implementations.

Provides:
- Agent: Abstract base class with observe/act/learn lifecycle.
- RandomAgent: Acts randomly from a pool of action types.
- RuleBasedAgent: Executes prioritized condition→action rules.
- QLearningAgent: Tabular Q-learning with ε-greedy exploration.
"""

from __future__ import annotations

import abc
import random
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Action:
    """Represents an action taken by an agent."""

    type: str
    parameters: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


class Agent(abc.ABC):
    """Abstract base class for all simulation agents."""

    def __init__(self, agent_id: str, name: str = "") -> None:
        """Initialize this instance."""
        self.id = agent_id
        self.name = name or agent_id
        self.step_count: int = 0
        self._history: list[Action] = []

    @abc.abstractmethod
    def act(self, observation: dict[str, Any]) -> Action:
        """Decide on an action given the current observation."""

    def learn(self, reward: float) -> None:
        """Update internal state based on reward. Override in learning agents."""

    def reset(self) -> None:
        """Reset the agent to its initial state."""
        self.step_count = 0
        self._history.clear()

    def record_action(self, action: Action) -> None:
        """Record an action in the agent's history."""
        self._history.append(action)
        self.step_count += 1

    @property
    def history(self) -> list[Action]:
        """Return a copy of the action history."""
        return list(self._history)

    @property
    def last_action(self) -> Action | None:
        """Return the most recent action, or None."""
        return self._history[-1] if self._history else None

    def to_dict(self) -> dict[str, Any]:
        """Serialize agent state."""
        return {
            "id": self.id,
            "name": self.name,
            "type": type(self).__name__,
            "step_count": self.step_count,
            "history_length": len(self._history),
        }


# ─── Concrete Agents ───────────────────────────────────────────────────


class RandomAgent(Agent):
    """Agent that selects actions uniformly at random.

    Useful as a baseline or for stress-testing simulations.
    """

    def __init__(
        self,
        agent_id: str,
        action_types: list[str] | None = None,
        name: str = "",
    ) -> None:
        """Initialize this instance."""
        super().__init__(agent_id, name)
        self.action_types = action_types or ["move", "wait", "observe"]

    def act(self, observation: dict[str, Any]) -> Action:
        """act ."""
        return Action(type=random.choice(self.action_types))


class RuleBasedAgent(Agent):
    """Agent that executes the first matching rule from a priority list.

    Rules are (condition, action_type) tuples. Each condition is a callable
    that takes the observation dict and returns True/False.

    Example::

        agent = RuleBasedAgent("guard")
        agent.add_rule(lambda obs: obs.get("threat"), "defend")
        agent.add_rule(lambda obs: True, "patrol")  # default
    """

    def __init__(self, agent_id: str, name: str = "") -> None:
        """Initialize this instance."""
        super().__init__(agent_id, name)
        self._rules: list[tuple[Any, str]] = []

    def add_rule(
        self, condition: Any, action_type: str, params: dict[str, Any] | None = None
    ) -> None:
        """Add a condition→action rule (evaluated in order).

        Args:
            condition: Callable[[dict], bool] — returns True when the rule fires.
            action_type: Action type string to emit.
            params: Optional parameters to include in the Action.
        """
        self._rules.append((condition, action_type, params or {}))  # type: ignore[arg-type]

    def act(self, observation: dict[str, Any]) -> Action:
        """act ."""
        for condition, action_type, params in self._rules:  # type: ignore[misc]
            try:
                if condition(observation):
                    return Action(type=action_type, parameters=params)
            except Exception:
                continue
        return Action(type="idle")


class QLearningAgent(Agent):
    """Tabular Q-learning agent with ε-greedy exploration.

    Learns an action-value function Q(state, action) from (state, action, reward)
    transitions.

    Args:
        agent_id: Unique identifier.
        action_types: List of available action type strings.
        alpha: Learning rate (0–1).
        gamma: Discount factor (0–1).
        epsilon: Exploration rate (0–1). Decays multiplicatively each step.
        epsilon_decay: Per-step decay multiplier for epsilon.
        epsilon_min: Lower bound for epsilon.
    """

    def __init__(
        self,
        agent_id: str,
        action_types: list[str],
        alpha: float = 0.1,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        name: str = "",
    ) -> None:
        """Initialize this instance."""
        super().__init__(agent_id, name)
        self.action_types = action_types
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        self._q_table: dict[str, dict[str, float]] = defaultdict(
            lambda: dict.fromkeys(self.action_types, 0.0)
        )
        self._last_state: str | None = None
        self._last_action_type: str | None = None

    def _state_key(self, observation: dict[str, Any]) -> str:
        """Convert observation to a hashable state key."""
        # Simple: sort and stringify. Override for custom state representations.
        items = sorted((k, v) for k, v in observation.items() if isinstance(v, (int, float, str, bool)))
        return str(items)

    def act(self, observation: dict[str, Any]) -> Action:
        """act ."""
        state = self._state_key(observation)
        self._last_state = state

        # ε-greedy
        if random.random() < self.epsilon:
            action_type = random.choice(self.action_types)
        else:
            q_values = self._q_table[state]
            action_type = max(q_values, key=q_values.get)  # type: ignore[arg-type]

        self._last_action_type = action_type
        return Action(type=action_type)

    def learn(self, reward: float) -> None:
        """Update Q-value for the last (state, action) pair."""
        if self._last_state is None or self._last_action_type is None:
            return

        old_q = self._q_table[self._last_state][self._last_action_type]
        # Since we don't have next state here, use reward directly (1-step)
        new_q = old_q + self.alpha * (reward - old_q)
        self._q_table[self._last_state][self._last_action_type] = new_q

        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    @property
    def q_table_size(self) -> int:
        """Number of states in the Q-table."""
        return len(self._q_table)

    def get_q_values(self, observation: dict[str, Any]) -> dict[str, float]:
        """Return Q-values for the current state."""
        return dict(self._q_table[self._state_key(observation)])
