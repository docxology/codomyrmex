"""
Base agent classes for the collaboration module.

Provides abstract and concrete base implementations for collaborative agents.
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from collections.abc import Callable

from ..exceptions import AgentBusyError
from ..models import AgentStatus, Task, TaskResult
from ..protocols import AgentCapability, AgentMessage, AgentState, MessageType

logger = logging.getLogger(__name__)


class AbstractAgent(ABC):
    """
    Abstract base class defining the agent interface.

    All agent implementations must inherit from this class and implement
    the required abstract methods.
    """

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Unique identifier for this agent."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this agent."""
        pass

    @property
    @abstractmethod
    def state(self) -> AgentState:
        """Current state of the agent."""
        pass

    @abstractmethod
    async def process_task(self, task: Task) -> TaskResult:
        """Process a task and return a result."""
        pass

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """Get list of capability names this agent possesses."""
        pass

    @abstractmethod
    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        pass


class CollaborativeAgent(AbstractAgent):
    """
    Base implementation for collaborative agents.

    Provides common functionality for agents participating in swarm collaboration
    including messaging, lifecycle management, and task execution.

    Attributes:
        agent_id: Unique identifier for this agent.
        name: Human-readable agent name.
        capabilities: List of capabilities this agent possesses.
        state: Current agent state.
    """

    def __init__(
        self,
        agent_id: str | None = None,
        name: str = "Agent",
        capabilities: list[AgentCapability] | None = None,
    ):
        self._agent_id = agent_id or str(uuid.uuid4())
        self._name = name
        self._capabilities = capabilities or []
        self._state = AgentState.IDLE
        self._inbox: asyncio.Queue = asyncio.Queue()
        self._current_task: Task | None = None
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._last_heartbeat = datetime.now()
        self._message_handlers: dict[MessageType, Callable] = {}
        self._running = False

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> AgentState:
        return self._state

    @state.setter
    def state(self, value: AgentState):
        self._state = value

    def get_capabilities(self) -> list[str]:
        """Get list of capability names."""
        return [c.name for c in self._capabilities]

    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has a specific capability."""
        return any(c.name == capability_name for c in self._capabilities)

    def add_capability(self, capability: AgentCapability) -> None:
        """Add a capability to this agent."""
        if not self.has_capability(capability.name):
            self._capabilities.append(capability)
            logger.info(f"Agent {self.name} gained capability: {capability.name}")

    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        return AgentStatus(
            agent_id=self._agent_id,
            name=self._name,
            status=self._state.value,
            current_task_id=self._current_task.id if self._current_task else None,
            capabilities=self.get_capabilities(),
            tasks_completed=self._tasks_completed,
            tasks_failed=self._tasks_failed,
            last_heartbeat=self._last_heartbeat,
        )

    def update_heartbeat(self) -> None:
        """Update the last heartbeat timestamp."""
        self._last_heartbeat = datetime.now()

    async def receive_message(self) -> AgentMessage:
        """Receive a message from the inbox."""
        return await self._inbox.get()

    def add_message(self, message: AgentMessage) -> None:
        """Add a message to the inbox."""
        self._inbox.put_nowait(message)

    def register_handler(self, message_type: MessageType, handler: Callable) -> None:
        """Register a handler for a specific message type."""
        self._message_handlers[message_type] = handler

    async def process_messages(self) -> None:
        """Process messages from the inbox."""
        while self._running:
            try:
                message = await asyncio.wait_for(self._inbox.get(), timeout=1.0)
                handler = self._message_handlers.get(message.message_type)
                if handler:
                    await handler(message)
                else:
                    logger.warning(f"No handler for message type: {message.message_type}")
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def start(self) -> None:
        """Start the agent's message processing loop."""
        self._running = True
        self._state = AgentState.IDLE
        logger.info(f"Agent {self.name} ({self._agent_id}) started")

    async def stop(self) -> None:
        """Stop the agent."""
        self._running = False
        self._state = AgentState.TERMINATED
        logger.info(f"Agent {self.name} ({self._agent_id}) stopped")

    async def process_task(self, task: Task) -> TaskResult:
        """
        Process a task and return a result.

        This base implementation tracks task state and metrics.
        Subclasses should override _execute_task for actual work.
        """
        if self._state == AgentState.BUSY:
            raise AgentBusyError(
                self._agent_id,
                self._current_task.id if self._current_task else None
            )

        self._state = AgentState.BUSY
        self._current_task = task
        start_time = datetime.now()

        try:
            output = await self._execute_task(task)
            duration = (datetime.now() - start_time).total_seconds()
            self._tasks_completed += 1

            return TaskResult(
                task_id=task.id,
                success=True,
                output=output,
                duration=duration,
                agent_id=self._agent_id,
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self._tasks_failed += 1
            logger.error(f"Task {task.id} failed: {e}")

            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e),
                duration=duration,
                agent_id=self._agent_id,
            )
        finally:
            self._state = AgentState.IDLE
            self._current_task = None
            self.update_heartbeat()

    async def _execute_task(self, task: Task) -> Any:
        """
        Execute the actual task work.

        Subclasses should override this method to implement
        task-specific logic.
        """
        raise NotImplementedError("Subclasses must implement _execute_task")

    def to_dict(self) -> dict[str, Any]:
        """Serialize agent to dictionary."""
        return {
            "agent_id": self._agent_id,
            "name": self._name,
            "state": self._state.value,
            "capabilities": [c.to_dict() for c in self._capabilities],
            "tasks_completed": self._tasks_completed,
            "tasks_failed": self._tasks_failed,
        }


__all__ = [
    "AbstractAgent",
    "CollaborativeAgent",
]
