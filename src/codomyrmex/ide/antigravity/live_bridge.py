"""Live Agent Bridge — real-time bidirectional chat between agents.

Connects Antigravity to a Claude Code PAI instance (or any other agent)
via an :class:`AgentRelay` channel, with background polling, automatic
tool proxying, and session persistence.

Example — Antigravity side::

    >>> from codomyrmex.ide.antigravity.live_bridge import LiveAgentBridge
    >>> bridge = LiveAgentBridge("collab-session")
    >>> bridge.start()
    >>> bridge.send("Analyze the test failures in src/tests/")
    >>> # ... Claude Code responds asynchronously ...
    >>> bridge.stop()

Example — Claude Code side::

    >>> from codomyrmex.ide.antigravity.live_bridge import ClaudeCodeEndpoint
    >>> endpoint = ClaudeCodeEndpoint("collab-session")
    >>> endpoint.start()  # auto-responds to incoming messages
"""

from __future__ import annotations

import logging
import threading
import time
import warnings
from collections.abc import Callable
from typing import Any

try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from codomyrmex.ide.antigravity.agent_relay import (
    MSG_SYSTEM,
    AgentRelay,
    RelayMessage,
)

# =====================================================================
# Antigravity Side
# =====================================================================

class LiveAgentBridge:
    """Connects Antigravity to a remote agent via file-based relay.

    Runs a background polling thread that dispatches incoming messages
    to registered handlers and can auto-execute tool requests using
    the ``AntigravityToolProvider``.

    Attributes:
        relay: The underlying ``AgentRelay``.
        identity: This agent's identity string.
        poll_interval: Seconds between polls.
    """

    def __init__(
        self,
        channel_id: str,
        *,
        identity: str = "antigravity",
        poll_interval: float = 2.0,
        auto_execute_tools: bool = True,
    ) -> None:
        """Initialize the bridge.

        Args:
            channel_id: Relay channel to join.
            identity: This agent's sender name.
            poll_interval: Seconds between polls.
            auto_execute_tools: Automatically execute incoming tool requests.
        """
        self.relay = AgentRelay(channel_id)
        self.identity = identity
        self.poll_interval = poll_interval
        self.auto_execute_tools = auto_execute_tools

        self._cursor: int = 0
        self._running = False
        self._thread: threading.Thread | None = None

        # Callbacks
        self._on_message: list[Callable[[RelayMessage], None]] = []
        self._on_tool_request: list[Callable[[RelayMessage], Any]] = []

        # Message history (local view)
        self._received: list[RelayMessage] = []

    # ── Lifecycle ─────────────────────────────────────────────────

    def start(self) -> None:
        """Start background polling.

        Posts a system message announcing the agent and begins polling.
        """
        if self._running:
            return

        self._cursor = self.relay.get_latest_cursor()
        self._running = True
        self.relay.post_system(f"{self.identity} joined the channel")

        self._thread = threading.Thread(
            target=self._poll_loop,
            name=f"relay-{self.identity}",
            daemon=True,
        )
        self._thread.start()
        logger.info(f"LiveAgentBridge started: {self.identity} on {self.relay.channel_id}")

    def stop(self) -> None:
        """Stop background polling."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=self.poll_interval * 2)
            self._thread = None
        self.relay.post_system(f"{self.identity} left the channel")
        logger.info(f"LiveAgentBridge stopped: {self.identity}")

    @property
    def is_running(self) -> bool:
        """Whether the polling thread is active."""
        return self._running

    # ── Sending ───────────────────────────────────────────────────

    def send(self, message: str, **metadata: Any) -> RelayMessage:
        """Send a chat message to the relay.

        Args:
            message: Message text.
            **metadata: Additional metadata.

        Returns:
            The posted ``RelayMessage``.
        """
        return self.relay.post_message(self.identity, message, metadata=metadata)

    def request_tool(
        self,
        tool_name: str,
        *,
        timeout: float = 30.0,
        **tool_args: Any,
    ) -> RelayMessage | None:
        """Request remote tool execution and wait for the result.

        Args:
            tool_name: Tool to execute.
            timeout: Seconds to wait for result.
            **tool_args: Tool arguments.

        Returns:
            The ``tool_result`` message, or None if timed out.
        """
        cursor = self.relay.get_latest_cursor()
        req = self.relay.post_tool_request(
            self.identity, tool_name, tool_args,
        )
        return self.relay.await_response(
            req.id,
            timeout=timeout,
            since_cursor=cursor,
        )

    # ── Callbacks ─────────────────────────────────────────────────

    def on_message(self, handler: Callable[[RelayMessage], None]) -> None:
        """Register a handler for incoming chat messages.

        Args:
            handler: Callable receiving a ``RelayMessage``.
        """
        self._on_message.append(handler)

    def on_tool_request(self, handler: Callable[[RelayMessage], Any]) -> None:
        """Register a handler for incoming tool requests.

        Args:
            handler: Callable receiving a ``RelayMessage``, returning the result.
        """
        self._on_tool_request.append(handler)

    # ── Polling ───────────────────────────────────────────────────

    def _poll_loop(self) -> None:
        """Background polling loop."""
        while self._running:
            try:
                self._poll_once()
            except Exception as e:
                logger.error(f"Poll error: {e}")
            time.sleep(self.poll_interval)

    def _poll_once(self) -> None:
        """Single poll iteration."""
        messages = self.relay.poll_messages(since_cursor=self._cursor)

        for msg in messages:
            # Skip own messages
            if msg.sender == self.identity:
                self._cursor = max(self._cursor, msg.cursor)
                continue

            self._received.append(msg)
            self._cursor = max(self._cursor, msg.cursor)

            # Dispatch by type
            if msg.is_chat:
                self._handle_chat(msg)
            elif msg.is_tool_request:
                self._handle_tool_request(msg)
            elif msg.is_tool_result:
                pass  # handled by await_response
            elif msg.msg_type == MSG_SYSTEM:
                logger.info(f"[system] {msg.content}")

    def _handle_chat(self, msg: RelayMessage) -> None:
        """Dispatch a chat message to registered handlers."""
        logger.info(f"[{msg.sender}] {msg.content[:100]}")
        for handler in self._on_message:
            try:
                handler(msg)
            except Exception as e:
                logger.error(f"Message handler error: {e}")

    def _handle_tool_request(self, msg: RelayMessage) -> None:
        """Handle an incoming tool request."""
        logger.info(f"[{msg.sender}] requests tool: {msg.tool_name}")

        # Try custom handlers first
        for handler in self._on_tool_request:
            try:
                result = handler(msg)
                self.relay.post_tool_result(self.identity, msg.id, result)
                return
            except Exception as e:
                logger.error(f"Tool request handler error: {e}")

        # Auto-execute via AntigravityToolProvider
        if self.auto_execute_tools and msg.tool_name:
            self._auto_execute_tool(msg)

    def _auto_execute_tool(self, msg: RelayMessage) -> None:
        """Auto-execute a tool request using AntigravityToolProvider."""
        try:
            from codomyrmex.ide.antigravity.tool_provider import (
                SAFE_TOOLS,
            )

            # Safety check: only auto-execute safe tools
            if msg.tool_name not in SAFE_TOOLS:
                self.relay.post_tool_result(
                    self.identity,
                    msg.id,
                    None,
                    error=f"Auto-execution denied for non-safe tool: {msg.tool_name}",
                )
                return

            from codomyrmex.ide.antigravity import AntigravityClient
            client = AntigravityClient()
            result = client.invoke_tool(msg.tool_name, msg.tool_args or {})
            self.relay.post_tool_result(self.identity, msg.id, str(result))

        except Exception as e:
            self.relay.post_tool_result(
                self.identity, msg.id, None, error=str(e),
            )

    # ── Accessors ─────────────────────────────────────────────────

    def get_received(
        self,
        *,
        limit: int | None = None,
        msg_type: str | None = None,
    ) -> list[RelayMessage]:
        """Get received messages.

        Args:
            limit: Max messages to return.
            msg_type: Filter by type.

        Returns:
            List of received messages.
        """
        msgs = self._received
        if msg_type:
            msgs = [m for m in msgs if m.msg_type == msg_type]
        if limit:
            msgs = msgs[-limit:]
        return msgs

    def get_stats(self) -> dict[str, Any]:
        """Get bridge statistics."""
        return {
            "identity": self.identity,
            "channel_id": self.relay.channel_id,
            "running": self._running,
            "cursor": self._cursor,
            "received_count": len(self._received),
            "relay_stats": self.relay.get_stats(),
        }


# =====================================================================
# Claude Code Side
# =====================================================================

class ClaudeCodeEndpoint:
    """Connects a Claude Code instance to the relay channel.

    .. deprecated::
        Use :class:`~codomyrmex.ide.antigravity.relay_endpoint.RelayEndpoint`
        instead.  ``RelayEndpoint`` accepts any LLM client (Ollama, Claude,
        etc.) and integrates the ``MessageScheduler`` for rate limiting.

    Polls for incoming messages and either auto-responds via
    ``ClaudeClient.execute_with_session()`` or dispatches to handlers.

    Attributes:
        relay: The underlying ``AgentRelay``.
        identity: This endpoint's identity string.
    """

    def __init__(
        self,
        channel_id: str,
        *,
        claude_client: Any | None = None,
        identity: str = "claude_code",
        poll_interval: float = 2.0,
        auto_respond: bool = True,
        model: str | None = None,
    ) -> None:
        """Initialize the Claude Code endpoint.

        .. deprecated::
            Use :class:`~codomyrmex.ide.antigravity.relay_endpoint.RelayEndpoint`
            instead.

        Args:
            channel_id: Relay channel to join.
            claude_client: A ``ClaudeClient`` instance. Lazy-created if None.
            identity: Sender identity.
            poll_interval: Seconds between polls.
            auto_respond: Automatically respond to chat messages.
            model: Claude model to use (default from client config).
        """
        warnings.warn(
            "ClaudeCodeEndpoint is deprecated; use "
            "codomyrmex.ide.antigravity.relay_endpoint.RelayEndpoint instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.relay = AgentRelay(channel_id)
        self.identity = identity
        self.poll_interval = poll_interval
        self.auto_respond = auto_respond
        self.model = model

        self._client = claude_client
        self._session = None
        self._cursor: int = 0
        self._running = False
        self._thread: threading.Thread | None = None

        # Custom handlers
        self._on_message: list[Callable[[RelayMessage], str | None]] = []

    @property
    def client(self) -> Any:
        """Lazy-initialize ClaudeClient.

        Returns:
            ClaudeClient instance.
        """
        if self._client is None:
            from codomyrmex.agents.claude.claude_client import ClaudeClient
            config = {}
            if self.model:
                config["model"] = self.model
            self._client = ClaudeClient(config=config)
        return self._client

    @property
    def session(self) -> Any:
        """Get or create the conversation session.

        Returns:
            AgentSession instance.
        """
        if self._session is None:
            self._session = self.client.create_session(
                session_id=f"relay-{self.relay.channel_id}",
            )
        return self._session

    # ── Lifecycle ─────────────────────────────────────────────────

    def start(self) -> None:
        """Start the endpoint polling loop."""
        if self._running:
            return

        self._cursor = self.relay.get_latest_cursor()
        self._running = True
        self.relay.post_system(f"{self.identity} joined the channel")

        self._thread = threading.Thread(
            target=self._poll_loop,
            name=f"relay-{self.identity}",
            daemon=True,
        )
        self._thread.start()
        logger.info(f"ClaudeCodeEndpoint started on {self.relay.channel_id}")

    def stop(self) -> None:
        """Stop the endpoint."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=self.poll_interval * 2)
            self._thread = None
        self.relay.post_system(f"{self.identity} left the channel")
        logger.info("ClaudeCodeEndpoint stopped")

    @property
    def is_running(self) -> bool:
        """Execute Is Running operations natively."""
        return self._running

    # ── Callbacks ─────────────────────────────────────────────────

    def on_message(self, handler: Callable[[RelayMessage], str | None]) -> None:
        """Register a handler for incoming messages.

        Handler should return a response string, or None to skip.

        Args:
            handler: Message handler.
        """
        self._on_message.append(handler)

    # ── Sending ───────────────────────────────────────────────────

    def send(self, message: str, **metadata: Any) -> RelayMessage:
        """Send a chat message.

        Args:
            message: Message text.
            **metadata: Additional metadata.

        Returns:
            Posted message.
        """
        return self.relay.post_message(self.identity, message, metadata=metadata)

    # ── Polling ───────────────────────────────────────────────────

    def _poll_loop(self) -> None:
        """Background polling loop."""
        while self._running:
            try:
                self._poll_once()
            except Exception as e:
                logger.error(f"ClaudeCode poll error: {e}")
            time.sleep(self.poll_interval)

    def _poll_once(self) -> None:
        """Single poll iteration."""
        messages = self.relay.poll_messages(since_cursor=self._cursor)

        for msg in messages:
            if msg.sender == self.identity:
                self._cursor = max(self._cursor, msg.cursor)
                continue

            self._cursor = max(self._cursor, msg.cursor)

            if msg.is_chat:
                self._handle_chat(msg)
            elif msg.is_tool_request:
                self._handle_tool_request(msg)

    def _handle_chat(self, msg: RelayMessage) -> None:
        """Process an incoming chat message."""
        logger.info(f"[{msg.sender}] {msg.content[:100]}")

        # Try custom handlers
        for handler in self._on_message:
            try:
                response = handler(msg)
                if response:
                    self.relay.post_message(self.identity, response)
                    return
            except Exception as e:
                logger.error(f"Message handler error: {e}")

        # Auto-respond via Claude API
        if self.auto_respond:
            self._auto_respond(msg)

    def _auto_respond(self, msg: RelayMessage) -> None:
        """Generate and post a Claude response."""
        try:
            from codomyrmex.agents.core import AgentRequest

            request = AgentRequest(
                prompt=msg.content,
                context=msg.metadata,
            )

            response = self.client.execute_with_session(
                request,
                session=self.session,
            )

            if response.is_success():
                self.relay.post_message(
                    self.identity,
                    response.content,
                    metadata={
                        "tokens_used": response.tokens_used,
                        "model": self.model or "default",
                        "in_reply_to": msg.id,
                    },
                )
            else:
                self.relay.post_message(
                    self.identity,
                    f"Error: {response.error}",
                    metadata={"error": True, "in_reply_to": msg.id},
                )

        except Exception as e:
            logger.error(f"Auto-respond failed: {e}")
            self.relay.post_message(
                self.identity,
                f"[error] Failed to generate response: {e}",
                metadata={"error": True, "in_reply_to": msg.id},
            )

    def _handle_tool_request(self, msg: RelayMessage) -> None:
        """Execute a tool request via the MCP bridge."""
        try:
            from codomyrmex.agents.pai.mcp_bridge import call_tool

            result = call_tool(msg.tool_name, **(msg.tool_args or {}))
            self.relay.post_tool_result(self.identity, msg.id, result)

        except Exception as e:
            self.relay.post_tool_result(
                self.identity, msg.id, None, error=str(e),
            )


__all__ = [
    "LiveAgentBridge",
    "ClaudeCodeEndpoint",
]
