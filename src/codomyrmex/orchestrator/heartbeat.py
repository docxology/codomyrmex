"""Heartbeat monitor for agent liveness detection.

Periodic heartbeat tracking with configurable timeout.
Missed beats trigger supervisor notification.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class AgentStatus(Enum):
    """Agent health status."""

    HEALTHY = "healthy"
    SUSPECT = "suspect"
    DEAD = "dead"
    UNKNOWN = "unknown"


@dataclass
class HeartbeatRecord:
    """Single heartbeat record.

    Attributes:
        agent_id: Agent identifier.
        timestamp: When the heartbeat was received.
        sequence: Heartbeat sequence number.
        metadata: Additional health data.
    """

    agent_id: str
    timestamp: float = field(default_factory=time.time)
    sequence: int = 0
    metadata: dict = field(default_factory=dict)


class HeartbeatMonitor:
    """Monitor agent liveness via periodic heartbeats.

    Example::

        monitor = HeartbeatMonitor(timeout_seconds=5.0)
        monitor.register("agent-1")
        monitor.beat("agent-1")
        status = monitor.check("agent-1")
    """

    def __init__(self, timeout_seconds: float = 10.0, suspect_threshold: int = 2) -> None:
        self._timeout = timeout_seconds
        self._suspect_threshold = suspect_threshold
        self._agents: dict[str, list[HeartbeatRecord]] = {}
        self._last_beat: dict[str, float] = {}
        self._missed_counts: dict[str, int] = {}

    @property
    def agent_count(self) -> int:
        return len(self._agents)

    def register(self, agent_id: str) -> None:
        """Register an agent for monitoring."""
        self._agents[agent_id] = []
        self._last_beat[agent_id] = time.time()
        self._missed_counts[agent_id] = 0

    def unregister(self, agent_id: str) -> bool:
        """Remove an agent from monitoring."""
        removed = agent_id in self._agents
        self._agents.pop(agent_id, None)
        self._last_beat.pop(agent_id, None)
        self._missed_counts.pop(agent_id, None)
        return removed

    def beat(self, agent_id: str, metadata: dict | None = None) -> None:
        """Record a heartbeat from an agent.

        Args:
            agent_id: Agent sending the heartbeat.
            metadata: Optional health data.
        """
        if agent_id not in self._agents:
            self.register(agent_id)

        seq = len(self._agents[agent_id]) + 1
        record = HeartbeatRecord(
            agent_id=agent_id,
            sequence=seq,
            metadata=metadata or {},
        )
        self._agents[agent_id].append(record)
        self._last_beat[agent_id] = record.timestamp
        self._missed_counts[agent_id] = 0

    def check(self, agent_id: str) -> AgentStatus:
        """Check the health status of an agent.

        Args:
            agent_id: Agent to check.

        Returns:
            AgentStatus based on last heartbeat timing.
        """
        if agent_id not in self._agents:
            return AgentStatus.UNKNOWN

        elapsed = time.time() - self._last_beat.get(agent_id, 0)

        if elapsed <= self._timeout:
            return AgentStatus.HEALTHY
        elif elapsed <= self._timeout * 2:
            return AgentStatus.SUSPECT
        else:
            return AgentStatus.DEAD

    def check_all(self) -> dict[str, AgentStatus]:
        """Check health of all registered agents."""
        return {aid: self.check(aid) for aid in self._agents}

    def dead_agents(self) -> list[str]:
        """Return IDs of agents considered dead."""
        return [
            aid for aid in self._agents
            if self.check(aid) == AgentStatus.DEAD
        ]

    def history(self, agent_id: str, n: int = 10) -> list[HeartbeatRecord]:
        """Get recent heartbeat history."""
        records = self._agents.get(agent_id, [])
        return records[-n:]


__all__ = ["AgentStatus", "HeartbeatMonitor", "HeartbeatRecord"]
