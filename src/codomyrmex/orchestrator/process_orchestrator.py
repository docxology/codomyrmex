"""Multi-process agent orchestrator.

Manages agent lifecycle: spawn, communicate, monitor, and
recover across processes using serialization and heartbeats.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.orchestrator.agent_supervisor import (
    AgentSupervisor,
    SupervisorAction,
)
from codomyrmex.orchestrator.heartbeat import HeartbeatMonitor


class ProcessState(Enum):
    """Agent process state."""

    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    CRASHED = "crashed"


@dataclass
class AgentProcess:
    """Metadata for a managed agent process.

    Attributes:
        agent_id: Unique agent identifier.
        agent_type: Agent class name.
        config: Agent configuration.
        state: Current process state.
        started_at: Process start time.
        pid: Process identifier (simulated).
    """

    agent_id: str
    agent_type: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    state: ProcessState = ProcessState.STOPPED
    started_at: float = 0.0
    pid: int = 0


@dataclass
class OrchestratorHealth:
    """Health summary of the orchestrator.

    Attributes:
        total_agents: Number of managed agents.
        running: Number running.
        stopped: Number stopped.
        crashed: Number crashed.
        agent_statuses: Per-agent status.
    """

    total_agents: int = 0
    running: int = 0
    stopped: int = 0
    crashed: int = 0
    agent_statuses: dict[str, str] = field(default_factory=dict)


class ProcessOrchestrator:
    """Manage agent processes with monitoring and recovery.

    Example::

        orchestrator = ProcessOrchestrator()
        agent_id = orchestrator.spawn("ThinkingAgent", {"depth": 3})
        health = orchestrator.health()
        orchestrator.shutdown_all()
    """

    def __init__(
        self,
        supervisor: AgentSupervisor | None = None,
        heartbeat: HeartbeatMonitor | None = None,
    ) -> None:
        """Execute   Init   operations natively."""
        self._supervisor = supervisor or AgentSupervisor()
        self._heartbeat = heartbeat or HeartbeatMonitor()
        self._agents: dict[str, AgentProcess] = {}
        self._next_pid = 1000

    @property
    def agent_count(self) -> int:
        """Execute Agent Count operations natively."""
        return len(self._agents)

    def spawn(
        self,
        agent_type: str,
        config: dict[str, Any] | None = None,
        agent_id: str = "",
    ) -> str:
        """Spawn a new agent process.

        Args:
            agent_type: Agent class name.
            config: Agent configuration.
            agent_id: Optional explicit ID.

        Returns:
            The agent's unique identifier.
        """
        if not agent_id:
            agent_id = f"agent-{uuid.uuid4().hex[:8]}"

        process = AgentProcess(
            agent_id=agent_id,
            agent_type=agent_type,
            config=config or {},
            state=ProcessState.RUNNING,
            started_at=time.time(),
            pid=self._next_pid,
        )
        self._next_pid += 1
        self._agents[agent_id] = process
        self._supervisor.register(agent_id)
        self._heartbeat.register(agent_id)
        self._heartbeat.beat(agent_id)

        return agent_id

    def shutdown(self, agent_id: str) -> bool:
        """Stop a specific agent.

        Args:
            agent_id: Agent to stop.

        Returns:
            True if stopped.
        """
        process = self._agents.get(agent_id)
        if process is None:
            return False

        process.state = ProcessState.STOPPED
        self._heartbeat.unregister(agent_id)
        return True

    def shutdown_all(self) -> int:
        """Stop all agents. Returns count stopped."""
        count = 0
        for aid in list(self._agents.keys()):
            if self.shutdown(aid):
                count += 1
        return count

    def send(self, agent_id: str, request: dict[str, Any]) -> bool:
        """Send a request to an agent.

        Args:
            agent_id: Target agent.
            request: Request payload.

        Returns:
            True if sent (agent is running).
        """
        process = self._agents.get(agent_id)
        if process is None or process.state != ProcessState.RUNNING:
            return False
        # In a real impl, this would send via IPC/transport
        return True

    def report_crash(self, agent_id: str, error: str) -> SupervisorAction:
        """Report an agent crash to the supervisor.

        Args:
            agent_id: Crashed agent.
            error: Error description.

        Returns:
            Action taken by the supervisor.
        """
        process = self._agents.get(agent_id)
        if process:
            process.state = ProcessState.CRASHED

        action = self._supervisor.on_agent_crash(agent_id, error)

        if action == SupervisorAction.RESTART:
            # Restart the agent
            if process:
                process.state = ProcessState.RUNNING
                process.started_at = time.time()
                self._heartbeat.beat(agent_id)

        return action

    def health(self) -> OrchestratorHealth:
        """Get health summary of all agents."""
        statuses: dict[str, str] = {}
        running = stopped = crashed = 0

        for aid, process in self._agents.items():
            statuses[aid] = process.state.value
            if process.state == ProcessState.RUNNING:
                running += 1
            elif process.state == ProcessState.STOPPED:
                stopped += 1
            elif process.state == ProcessState.CRASHED:
                crashed += 1

        return OrchestratorHealth(
            total_agents=len(self._agents),
            running=running,
            stopped=stopped,
            crashed=crashed,
            agent_statuses=statuses,
        )

    def running_agents(self) -> list[str]:
        """Get IDs of currently running agents."""
        return [
            aid for aid, p in self._agents.items()
            if p.state == ProcessState.RUNNING
        ]


__all__ = ["AgentProcess", "OrchestratorHealth", "ProcessOrchestrator", "ProcessState"]
