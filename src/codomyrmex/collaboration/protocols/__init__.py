"""
Multi-agent coordination protocols.

Provides protocols and utilities for agent collaboration and swarm behavior.
"""

import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class AgentState(Enum):
    """States an agent can be in."""
    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    ERROR = "error"
    TERMINATED = "terminated"


class MessageType(Enum):
    """Types of messages between agents."""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    HANDOFF = "handoff"
    STATUS = "status"
    ERROR = "error"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    receiver_id: str | None = None  # None = broadcast
    message_type: MessageType = MessageType.REQUEST
    content: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    reply_to: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "reply_to": self.reply_to,
        }

    def create_reply(self, content: Any, **metadata) -> 'AgentMessage':
        """Create a reply to this message."""
        return AgentMessage(
            sender_id=self.receiver_id or "",
            receiver_id=self.sender_id,
            message_type=MessageType.RESPONSE,
            content=content,
            metadata=metadata,
            reply_to=self.id,
        )


@dataclass
class AgentCapability:
    """A capability that an agent possesses."""
    name: str
    description: str
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }


class AgentProtocol(ABC):
    """Abstract base class for agent coordination protocols."""

    @abstractmethod
    async def execute(self, task: Any, agents: list['BaseAgent']) -> Any:
        """Execute the protocol with the given agents."""
        pass

    @abstractmethod
    def select_agents(self, task: Any, available_agents: list['BaseAgent']) -> list['BaseAgent']:
        """Select agents for a task."""
        pass


class BaseAgent(ABC):
    """Base class for collaborative agents."""

    def __init__(
        self,
        agent_id: str | None = None,
        name: str = "Agent",
        capabilities: list[AgentCapability] | None = None,
    ):
        """Execute   Init   operations natively."""
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name
        self.capabilities = capabilities or []
        self.state = AgentState.IDLE
        self._inbox: asyncio.Queue = asyncio.Queue()
        self._message_handlers: dict[MessageType, Callable] = {}

    @abstractmethod
    async def process_task(self, task: Any) -> Any:
        """Process a task and return a result."""
        pass

    async def send_message(self, message: AgentMessage, coordinator: 'AgentCoordinator') -> None:
        """Send a message through the coordinator."""
        message.sender_id = self.agent_id
        await coordinator.route_message(message)

    async def receive_message(self) -> AgentMessage:
        """Receive a message from the inbox."""
        return await self._inbox.get()

    def add_message(self, message: AgentMessage) -> None:
        """Add a message to the inbox."""
        self._inbox.put_nowait(message)

    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has a specific capability."""
        return any(c.name == capability_name for c in self.capabilities)

    def get_capabilities(self) -> list[str]:
        """Get list of capability names."""
        return [c.name for c in self.capabilities]

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state.value,
            "capabilities": [c.to_dict() for c in self.capabilities],
        }


class AgentCoordinator:
    """Coordinates communication and task distribution between agents."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self.agents: dict[str, BaseAgent] = {}
        self.message_log: list[AgentMessage] = []
        self.protocols: dict[str, AgentProtocol] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the coordinator."""
        self.agents[agent.agent_id] = agent

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]

    def register_protocol(self, name: str, protocol: AgentProtocol) -> None:
        """Register a coordination protocol."""
        self.protocols[name] = protocol

    async def route_message(self, message: AgentMessage) -> None:
        """Route a message to the appropriate agent(s)."""
        self.message_log.append(message)

        if message.receiver_id:
            # Direct message
            if message.receiver_id in self.agents:
                self.agents[message.receiver_id].add_message(message)
        else:
            # Broadcast
            for agent_id, agent in self.agents.items():
                if agent_id != message.sender_id:
                    agent.add_message(message)

    async def execute_protocol(self, protocol_name: str, task: Any) -> Any:
        """Execute a coordination protocol."""
        if protocol_name not in self.protocols:
            raise ValueError(f"Unknown protocol: {protocol_name}")

        protocol = self.protocols[protocol_name]
        available_agents = list(self.agents.values())
        selected_agents = protocol.select_agents(task, available_agents)

        return await protocol.execute(task, selected_agents)

    def find_agents_with_capability(self, capability: str) -> list[BaseAgent]:
        """Find all agents with a specific capability."""
        return [a for a in self.agents.values() if a.has_capability(capability)]

    def get_idle_agents(self) -> list[BaseAgent]:
        """Get all idle agents."""
        return [a for a in self.agents.values() if a.state == AgentState.IDLE]


class RoundRobinProtocol(AgentProtocol):
    """Distributes tasks to agents in round-robin fashion."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self._current_index = 0

    def select_agents(self, task: Any, available_agents: list[BaseAgent]) -> list[BaseAgent]:
        """Execute Select Agents operations natively."""
        if not available_agents:
            return []

        agent = available_agents[self._current_index % len(available_agents)]
        self._current_index += 1
        return [agent]

    async def execute(self, task: Any, agents: list[BaseAgent]) -> Any:
        if not agents:
            raise ValueError("No agents available")

        agent = agents[0]
        agent.state = AgentState.BUSY
        try:
            result = await agent.process_task(task)
            return result
        finally:
            agent.state = AgentState.IDLE


class BroadcastProtocol(AgentProtocol):
    """Broadcasts task to all agents and collects results."""

    def select_agents(self, task: Any, available_agents: list[BaseAgent]) -> list[BaseAgent]:
        """Execute Select Agents operations natively."""
        return available_agents

    async def execute(self, task: Any, agents: list[BaseAgent]) -> list[Any]:
        tasks = []
        for agent in agents:
            agent.state = AgentState.BUSY
            tasks.append(agent.process_task(task))

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        finally:
            for agent in agents:
                agent.state = AgentState.IDLE


class CapabilityRoutingProtocol(AgentProtocol):
    """Routes tasks to agents based on required capabilities."""

    def __init__(self, required_capability: str):
        """Execute   Init   operations natively."""
        self.required_capability = required_capability

    def select_agents(self, task: Any, available_agents: list[BaseAgent]) -> list[BaseAgent]:
        """Execute Select Agents operations natively."""
        return [a for a in available_agents if a.has_capability(self.required_capability)]

    async def execute(self, task: Any, agents: list[BaseAgent]) -> Any:
        if not agents:
            raise ValueError(f"No agents with capability: {self.required_capability}")

        # Use first available agent
        agent = next((a for a in agents if a.state == AgentState.IDLE), agents[0])
        agent.state = AgentState.BUSY

        try:
            return await agent.process_task(task)
        finally:
            agent.state = AgentState.IDLE


class ConsensusProtocol(AgentProtocol):
    """Requires consensus among agents for task completion."""

    def __init__(self, quorum: float = 0.5):
        """Execute   Init   operations natively."""
        self.quorum = quorum  # Percentage of agents that must agree

    def select_agents(self, task: Any, available_agents: list[BaseAgent]) -> list[BaseAgent]:
        """Execute Select Agents operations natively."""
        return available_agents

    async def execute(self, task: Any, agents: list[BaseAgent]) -> Any:
        if not agents:
            raise ValueError("No agents available for consensus")

        # Get results from all agents
        tasks = [agent.process_task(task) for agent in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors
        valid_results = [r for r in results if not isinstance(r, Exception)]

        if not valid_results:
            raise ValueError("All agents failed")

        # Simple consensus: most common result
        result_counts: dict[str, int] = {}
        for result in valid_results:
            key = json.dumps(result, sort_keys=True, default=str)
            result_counts[key] = result_counts.get(key, 0) + 1

        # Check if quorum is met
        max_count = max(result_counts.values())
        if max_count / len(agents) >= self.quorum:
            max_key = max(result_counts.keys(), key=lambda k: result_counts[k])
            return json.loads(max_key)

        raise ValueError("Consensus not reached")


__all__ = [
    "AgentState",
    "MessageType",
    "AgentMessage",
    "AgentCapability",
    "AgentProtocol",
    "BaseAgent",
    "AgentCoordinator",
    "RoundRobinProtocol",
    "BroadcastProtocol",
    "CapabilityRoutingProtocol",
    "ConsensusProtocol",
]
