"""
Direct messaging for point-to-point communication.

Provides request-response patterns and direct agent-to-agent messaging.
"""

import asyncio
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from ..exceptions import MessageDeliveryError
from ..protocols import AgentMessage, MessageType

logger = get_logger(__name__)


@dataclass
class PendingRequest:
    """A pending request awaiting a response."""
    request_id: str
    sender_id: str
    receiver_id: str
    message: AgentMessage
    future: asyncio.Future
    timeout: float
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_expired(self) -> bool:
        """Check if the request has expired."""
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.timeout


class DirectMessenger:
    """
    Direct messenger for point-to-point agent communication.

    Supports both fire-and-forget messages and request-response patterns
    with timeout handling.

    Attributes:
        default_timeout: Default timeout for requests in seconds.
    """

    def __init__(self, default_timeout: float = 30.0):
        self._handlers: dict[str, Callable[[AgentMessage], Awaitable[Any]]] = {}
        self._pending_requests: dict[str, PendingRequest] = {}
        self._default_timeout = default_timeout
        self._message_log: list[AgentMessage] = []
        self._max_log_size = 1000

    def register_handler(
        self,
        agent_id: str,
        handler: Callable[[AgentMessage], Awaitable[Any]],
    ) -> None:
        """
        Register a message handler for an agent.

        Args:
            agent_id: ID of the agent receiving messages.
            handler: Async function to handle incoming messages.
        """
        self._handlers[agent_id] = handler
        logger.info(f"Registered message handler for agent: {agent_id}")

    def unregister_handler(self, agent_id: str) -> bool:
        """Unregister a message handler."""
        if agent_id in self._handlers:
            del self._handlers[agent_id]
            return True
        return False

    async def send(
        self,
        sender_id: str,
        receiver_id: str,
        content: Any,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Send a message to another agent (fire-and-forget).

        Args:
            sender_id: ID of the sending agent.
            receiver_id: ID of the receiving agent.
            content: Message content.
            metadata: Optional message metadata.

        Raises:
            MessageDeliveryError: If the receiver has no registered handler.
        """
        if receiver_id not in self._handlers:
            raise MessageDeliveryError(
                str(uuid.uuid4()),
                sender_id,
                receiver_id,
                "No handler registered for receiver"
            )

        message = AgentMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=MessageType.REQUEST,
            content=content,
            metadata=metadata or {},
        )

        self._log_message(message)

        try:
            handler = self._handlers[receiver_id]
            if asyncio.iscoroutinefunction(handler):
                await handler(message)
            else:
                handler(message)
            logger.debug(f"Message delivered: {sender_id} -> {receiver_id}")
        except Exception as e:
            raise MessageDeliveryError(
                message.id,
                sender_id,
                receiver_id,
                str(e)
            ) from e

    async def request(
        self,
        sender_id: str,
        receiver_id: str,
        content: Any,
        timeout: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """
        Send a request and wait for a response.

        Args:
            sender_id: ID of the sending agent.
            receiver_id: ID of the receiving agent.
            content: Request content.
            timeout: Timeout in seconds (uses default if not specified).
            metadata: Optional message metadata.

        Returns:
            The response from the receiver.

        Raises:
            MessageDeliveryError: If delivery fails.
            asyncio.TimeoutError: If no response within timeout.
        """
        if receiver_id not in self._handlers:
            raise MessageDeliveryError(
                str(uuid.uuid4()),
                sender_id,
                receiver_id,
                "No handler registered for receiver"
            )

        timeout = timeout or self._default_timeout

        message = AgentMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=MessageType.REQUEST,
            content=content,
            metadata=metadata or {},
        )

        # Create pending request
        future: asyncio.Future = asyncio.Future()
        pending = PendingRequest(
            request_id=message.id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message,
            future=future,
            timeout=timeout,
        )
        self._pending_requests[message.id] = pending

        self._log_message(message)

        try:
            # Deliver the message
            handler = self._handlers[receiver_id]
            if asyncio.iscoroutinefunction(handler):
                result = await handler(message)
            else:
                result = handler(message)

            # If handler returned a value, use it as response
            if result is not None:
                return result

            # Otherwise wait for explicit response
            return await asyncio.wait_for(future, timeout)

        except TimeoutError:
            raise
        except Exception as e:
            raise MessageDeliveryError(
                message.id,
                sender_id,
                receiver_id,
                str(e)
            ) from e
        finally:
            # Cleanup pending request
            self._pending_requests.pop(message.id, None)

    async def respond(
        self,
        original_message: AgentMessage,
        content: Any,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Send a response to a request.

        Args:
            original_message: The message being responded to.
            content: Response content.
            metadata: Optional response metadata.
        """
        response = original_message.create_reply(content, **(metadata or {}))
        self._log_message(response)

        # Complete the pending request future if exists
        if original_message.id in self._pending_requests:
            pending = self._pending_requests[original_message.id]
            if not pending.future.done():
                pending.future.set_result(content)

    def _log_message(self, message: AgentMessage) -> None:
        """Log a message for auditing."""
        self._message_log.append(message)
        if len(self._message_log) > self._max_log_size:
            self._message_log.pop(0)

    def get_message_log(
        self,
        agent_id: str | None = None,
        limit: int = 100,
    ) -> list[AgentMessage]:
        """
        Get message log, optionally filtered by agent.

        Args:
            agent_id: Filter to messages involving this agent.
            limit: Maximum number of messages to return.

        Returns:
            List of messages, most recent first.
        """
        messages = self._message_log

        if agent_id:
            messages = [
                m for m in messages
                if m.sender_id == agent_id or m.receiver_id == agent_id
            ]

        return list(reversed(messages[-limit:]))

    def clear_expired_requests(self) -> int:
        """Clear expired pending requests. Returns count of cleared requests."""
        expired = [
            rid for rid, req in self._pending_requests.items()
            if req.is_expired
        ]

        for rid in expired:
            req = self._pending_requests.pop(rid)
            if not req.future.done():
                req.future.set_exception(TimeoutError("Request expired"))

        return len(expired)


class ConversationTracker:
    """
    Tracks conversations between agents.

    Groups related messages into conversations for context tracking.
    """

    def __init__(self):
        self._conversations: dict[str, list[AgentMessage]] = {}
        self._agent_conversations: dict[str, set[str]] = {}

    def start_conversation(
        self,
        participants: list[str],
        initial_message: AgentMessage | None = None,
    ) -> str:
        """Start a new conversation."""
        conversation_id = str(uuid.uuid4())
        self._conversations[conversation_id] = []

        for agent_id in participants:
            if agent_id not in self._agent_conversations:
                self._agent_conversations[agent_id] = set()
            self._agent_conversations[agent_id].add(conversation_id)

        if initial_message:
            self.add_message(conversation_id, initial_message)

        return conversation_id

    def add_message(self, conversation_id: str, message: AgentMessage) -> None:
        """Add a message to a conversation."""
        if conversation_id in self._conversations:
            self._conversations[conversation_id].append(message)

    def get_conversation(self, conversation_id: str) -> list[AgentMessage]:
        """Get all messages in a conversation."""
        return self._conversations.get(conversation_id, [])

    def get_agent_conversations(self, agent_id: str) -> list[str]:
        """Get all conversation IDs involving an agent."""
        return list(self._agent_conversations.get(agent_id, set()))

    def end_conversation(self, conversation_id: str) -> bool:
        """End a conversation."""
        if conversation_id in self._conversations:
            # Remove from agent mappings
            for agent_convos in self._agent_conversations.values():
                agent_convos.discard(conversation_id)
            del self._conversations[conversation_id]
            return True
        return False


__all__ = [
    "PendingRequest",
    "DirectMessenger",
    "ConversationTracker",
]
