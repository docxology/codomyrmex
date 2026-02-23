"""OTP-style agent supervisor with restart strategies.

Supervises agent processes with configurable restart
policies: one-for-one, one-for-all, rest-for-one.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RestartStrategy(Enum):
    """Supervision restart strategy."""

    ONE_FOR_ONE = "one_for_one"
    ONE_FOR_ALL = "one_for_all"
    REST_FOR_ONE = "rest_for_one"


class SupervisorAction(Enum):
    """Action taken by supervisor on crash."""

    RESTART = "restart"
    ESCALATE = "escalate"
    IGNORE = "ignore"


@dataclass
class CrashRecord:
    """Record of an agent crash.

    Attributes:
        agent_id: Crashed agent.
        error: Error description.
        timestamp: When the crash occurred.
        restart_count: Restarts since last window reset.
        action_taken: What the supervisor did.
    """

    agent_id: str
    error: str
    timestamp: float = field(default_factory=time.time)
    restart_count: int = 0
    action_taken: SupervisorAction = SupervisorAction.RESTART


class AgentSupervisor:
    """OTP-style agent supervisor.

    Manages agent restarts with configurable strategies
    and escalation policies.

    Example::

        supervisor = AgentSupervisor(
            strategy=RestartStrategy.ONE_FOR_ONE,
            max_restarts=3,
            restart_window=60.0,
        )
        supervisor.register("agent-1")
        action = supervisor.on_agent_crash("agent-1", "OOM")
    """

    def __init__(
        self,
        strategy: RestartStrategy = RestartStrategy.ONE_FOR_ONE,
        max_restarts: int = 3,
        restart_window: float = 60.0,
    ) -> None:
        self._strategy = strategy
        self._max_restarts = max_restarts
        self._restart_window = restart_window
        self._agents: dict[str, list[CrashRecord]] = {}
        self._registered: list[str] = []

    @property
    def strategy(self) -> RestartStrategy:
        return self._strategy

    @property
    def agent_count(self) -> int:
        return len(self._registered)

    def register(self, agent_id: str) -> None:
        """Register an agent for supervision."""
        if agent_id not in self._registered:
            self._registered.append(agent_id)
            self._agents[agent_id] = []

    def unregister(self, agent_id: str) -> bool:
        """Remove an agent from supervision."""
        if agent_id in self._registered:
            self._registered.remove(agent_id)
            self._agents.pop(agent_id, None)
            return True
        return False

    def on_agent_crash(self, agent_id: str, error: str) -> SupervisorAction:
        """Handle an agent crash according to strategy.

        Args:
            agent_id: The crashed agent.
            error: Error description.

        Returns:
            The action taken.
        """
        if agent_id not in self._agents:
            return SupervisorAction.IGNORE

        now = time.time()
        crashes = self._agents[agent_id]

        # Count recent crashes within window
        recent = [c for c in crashes if now - c.timestamp < self._restart_window]
        restart_count = len(recent) + 1

        # Determine action
        if restart_count > self._max_restarts:
            action = SupervisorAction.ESCALATE
        else:
            action = SupervisorAction.RESTART

        record = CrashRecord(
            agent_id=agent_id,
            error=error,
            restart_count=restart_count,
            action_taken=action,
        )
        crashes.append(record)

        # Apply strategy
        if action == SupervisorAction.RESTART:
            self._apply_strategy(agent_id)

        return action

    def crash_history(self, agent_id: str) -> list[CrashRecord]:
        """Get crash history for an agent."""
        return list(self._agents.get(agent_id, []))

    def agents_to_restart(self, crashed_agent_id: str) -> list[str]:
        """Determine which agents to restart based on strategy.

        Args:
            crashed_agent_id: The agent that crashed.

        Returns:
            List of agent IDs that should be restarted.
        """
        if self._strategy == RestartStrategy.ONE_FOR_ONE:
            return [crashed_agent_id]
        elif self._strategy == RestartStrategy.ONE_FOR_ALL:
            return list(self._registered)
        elif self._strategy == RestartStrategy.REST_FOR_ONE:
            try:
                idx = self._registered.index(crashed_agent_id)
                return self._registered[idx:]
            except ValueError:
                return [crashed_agent_id]
        return [crashed_agent_id]

    def _apply_strategy(self, crashed_id: str) -> None:
        """Apply the restart strategy (internal)."""
        agents_to_restart = self.agents_to_restart(crashed_id)
        for p_id in agents_to_restart:
            if p_id != crashed_id and p_id in self._agents:
                self._agents[p_id].append(
                    CrashRecord(
                        agent_id=p_id, 
                        error=f"Cascaded restart due to {crashed_id}",
                        action_taken=SupervisorAction.RESTART
                    )
                )

    def total_crashes(self) -> int:
        """Total crashes across all agents."""
        return sum(len(records) for records in self._agents.values())


__all__ = [
    "AgentSupervisor",
    "CrashRecord",
    "RestartStrategy",
    "SupervisorAction",
]
