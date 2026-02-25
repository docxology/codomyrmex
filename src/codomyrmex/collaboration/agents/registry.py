"""
Agent registry for discovery and lifecycle management.

Provides centralized agent registration, lookup by capability,
and health monitoring functionality.
"""

import asyncio
import logging
import threading
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Optional

from ..exceptions import AgentNotFoundError
from ..models import AgentStatus, SwarmStatus
from ..protocols import AgentState
from .base import CollaborativeAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Centralized registry for agent discovery and management.

    The registry maintains a catalog of all agents in the system,
    enabling lookup by ID, capability, or state. It also monitors
    agent health through heartbeat tracking.

    Attributes:
        health_check_interval: Seconds between health checks.
        heartbeat_timeout: Seconds before an agent is considered unhealthy.
    """

    _instance: Optional["AgentRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        health_check_interval: float = 30.0,
        heartbeat_timeout: float = 60.0,
    ):
        """Execute   Init   operations natively."""
        if self._initialized:
            return

        self._agents: dict[str, CollaborativeAgent] = {}
        self._capability_index: dict[str, set[str]] = {}  # capability -> agent_ids
        self._health_check_interval = health_check_interval
        self._heartbeat_timeout = heartbeat_timeout
        self._health_check_task: asyncio.Task | None = None
        self._running = False
        self._listeners: list[Callable[[str, str], None]] = []  # (event, agent_id)
        self._started_at: datetime | None = None
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "AgentRegistry":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None

    def register(self, agent: CollaborativeAgent) -> str:
        """
        Register an agent with the registry.

        Args:
            agent: The agent to register.

        Returns:
            The agent's ID.
        """
        self._agents[agent.agent_id] = agent

        # Update capability index
        for capability in agent.get_capabilities():
            if capability not in self._capability_index:
                self._capability_index[capability] = set()
            self._capability_index[capability].add(agent.agent_id)

        logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")
        self._notify_listeners("registered", agent.agent_id)

        return agent.agent_id

    def unregister(self, agent_id: str) -> bool:
        """
        Unregister an agent from the registry.

        Args:
            agent_id: ID of the agent to unregister.

        Returns:
            True if the agent was found and removed.
        """
        if agent_id not in self._agents:
            return False

        agent = self._agents[agent_id]

        # Remove from capability index
        for capability in agent.get_capabilities():
            if capability in self._capability_index:
                self._capability_index[capability].discard(agent_id)
                if not self._capability_index[capability]:
                    del self._capability_index[capability]

        del self._agents[agent_id]
        logger.info(f"Unregistered agent: {agent_id}")
        self._notify_listeners("unregistered", agent_id)

        return True

    def get(self, agent_id: str) -> CollaborativeAgent:
        """
        Get an agent by ID.

        Raises:
            AgentNotFoundError: If the agent is not registered.
        """
        if agent_id not in self._agents:
            raise AgentNotFoundError(agent_id)
        return self._agents[agent_id]

    def get_all(self) -> list[CollaborativeAgent]:
        """Get all registered agents."""
        return list(self._agents.values())

    def find_by_capability(self, capability: str) -> list[CollaborativeAgent]:
        """Find all agents with a specific capability."""
        agent_ids = self._capability_index.get(capability, set())
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def find_by_capabilities(self, capabilities: list[str]) -> list[CollaborativeAgent]:
        """Find agents that have ALL specified capabilities."""
        if not capabilities:
            return self.get_all()

        # Start with agents having the first capability
        matching_ids = self._capability_index.get(capabilities[0], set()).copy()

        # Intersect with other capabilities
        for capability in capabilities[1:]:
            matching_ids &= self._capability_index.get(capability, set())

        return [self._agents[aid] for aid in matching_ids if aid in self._agents]

    def find_by_state(self, state: AgentState) -> list[CollaborativeAgent]:
        """Find all agents in a specific state."""
        return [a for a in self._agents.values() if a.state == state]

    def get_idle_agents(self) -> list[CollaborativeAgent]:
        """Get all agents in idle state."""
        return self.find_by_state(AgentState.IDLE)

    def get_status(self, agent_id: str) -> AgentStatus:
        """Get status of a specific agent."""
        return self.get(agent_id).get_status()

    def get_swarm_status(self) -> SwarmStatus:
        """Get overall swarm status."""
        agents = self.get_all()
        idle = len([a for a in agents if a.state == AgentState.IDLE])
        busy = len([a for a in agents if a.state == AgentState.BUSY])

        uptime = 0.0
        if self._started_at:
            uptime = (datetime.now() - self._started_at).total_seconds()

        return SwarmStatus(
            total_agents=len(agents),
            active_agents=busy,
            idle_agents=idle,
            uptime_seconds=uptime,
        )

    def add_listener(self, listener: Callable[[str, str], None]) -> None:
        """Add a listener for registry events (registered, unregistered, unhealthy)."""
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[str, str], None]) -> None:
        """Remove a listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify_listeners(self, event: str, agent_id: str) -> None:
        """Notify all listeners of an event."""
        for listener in self._listeners:
            try:
                listener(event, agent_id)
            except Exception as e:
                logger.error(f"Listener error: {e}")

    async def start_health_monitoring(self) -> None:
        """Start the health monitoring background task."""
        if self._running:
            return

        self._running = True
        self._started_at = datetime.now()
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Agent registry health monitoring started")

    async def stop_health_monitoring(self) -> None:
        """Stop the health monitoring background task."""
        self._running = False
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info("Agent registry health monitoring stopped")

    async def _health_check_loop(self) -> None:
        """Background loop for checking agent health."""
        while self._running:
            await asyncio.sleep(self._health_check_interval)
            await self._check_agent_health()

    async def _check_agent_health(self) -> None:
        """Check health of all registered agents."""
        now = datetime.now()
        timeout = timedelta(seconds=self._heartbeat_timeout)

        for agent_id, agent in list(self._agents.items()):
            status = agent.get_status()
            if now - status.last_heartbeat > timeout:
                logger.warning(f"Agent {agent_id} missed heartbeat")
                agent.state = AgentState.ERROR
                self._notify_listeners("unhealthy", agent_id)


def get_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    return AgentRegistry.get_instance()


__all__ = [
    "AgentRegistry",
    "get_registry",
]
