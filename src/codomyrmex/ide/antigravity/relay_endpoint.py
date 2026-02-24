"""Relay Endpoint --- provider-agnostic LLM relay for inter-agent chat.

A generic replacement for :class:`ClaudeCodeEndpoint` that accepts **any**
LLM client (Ollama, Claude, or custom) rather than hard-wiring to a single
provider.  The public API mirrors ``ClaudeCodeEndpoint`` so callers can
migrate with a single import-path change.

Example::

    >>> from codomyrmex.ide.antigravity.relay_endpoint import RelayEndpoint
    >>> endpoint = RelayEndpoint("collab-session")
    >>> endpoint.start()  # auto-responds via detected LLM
    >>> endpoint.send("Summarize the last test run")
    >>> endpoint.stop()
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from typing import Any

try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from codomyrmex.ide.antigravity.agent_relay import (
    AgentRelay,
    RelayMessage,
    MSG_CHAT,
    MSG_TOOL_REQUEST,
    MSG_SYSTEM,
)
from codomyrmex.agents.llm_client import get_llm_client, AgentRequest

# Optional scheduler support -- not yet available in all installations.
try:
    from codomyrmex.ide.antigravity.message_scheduler import (
        MessageScheduler,
        SchedulerConfig,
    )
except ImportError:  # pragma: no cover
    MessageScheduler = None  # type: ignore[assignment,misc]
    SchedulerConfig = None  # type: ignore[assignment,misc]


# =====================================================================
# RelayEndpoint
# =====================================================================

class RelayEndpoint:
    """Provider-agnostic LLM relay endpoint.

    Connects *any* LLM client to a file-based :class:`AgentRelay` channel
    with background polling, automatic chat responses, and MCP tool proxying.
    """

    def __init__(
        self,
        channel_id: str,
        *,
        llm_client: Any | None = None,
        identity: str = "agent",
        poll_interval: float = 2.0,
        auto_respond: bool = True,
        model: str | None = None,
        scheduler_config: Any | None = None,
    ) -> None:
        """Execute   Init   operations natively."""
        self.relay = AgentRelay(channel_id)
        self.identity = identity
        self.poll_interval = poll_interval
        self.auto_respond = auto_respond
        self.model = model

        self._llm_client = llm_client
        self._session: Any = None
        self._cursor: int = 0
        self._running = False
        self._thread: threading.Thread | None = None
        self._on_message: list[Callable[[RelayMessage], str | None]] = []

        # Scheduler (optional)
        self._scheduler: Any = None
        if scheduler_config is not None:
            if MessageScheduler is None:
                logger.warning(
                    "scheduler_config provided but MessageScheduler is not "
                    "installed -- falling back to direct sends"
                )
            else:
                self._scheduler = MessageScheduler(
                    self.relay, scheduler_config, identity=identity,
                )

    # ── Properties ────────────────────────────────────────────────

    @property
    def client(self) -> Any:
        """Lazy-init the LLM client via :func:`get_llm_client` if needed."""
        if self._llm_client is None:
            logger.info(f"Auto-detecting LLM client for identity={self.identity!r}")
            self._llm_client = get_llm_client(self.identity)
        return self._llm_client

    @property
    def session(self) -> Any:
        """Get or create a conversation session (if the client supports it)."""
        if self._session is None and hasattr(self.client, "create_session"):
            self._session = self.client.create_session(
                session_id=f"relay-{self.relay.channel_id}",
            )
        return self._session

    @property
    def is_running(self) -> bool:
        """Whether the background polling thread is active."""
        return self._running

    # ── Lifecycle ─────────────────────────────────────────────────

    def start(self) -> None:
        """Start background polling."""
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
        logger.info(f"RelayEndpoint started: {self.identity} on {self.relay.channel_id}")

    def stop(self) -> None:
        """Stop background polling and post a departure notice."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=self.poll_interval * 2)
            self._thread = None
        self.relay.post_system(f"{self.identity} left the channel")
        logger.info(f"RelayEndpoint stopped: {self.identity}")

    # ── Callbacks ─────────────────────────────────────────────────

    def on_message(self, handler: Callable[[RelayMessage], str | None]) -> None:
        """Register a handler for incoming chat messages.

        The handler should return a response string, or *None* to skip
        (letting auto-respond handle it).
        """
        self._on_message.append(handler)

    # ── Sending ───────────────────────────────────────────────────

    def send(self, message: str, **metadata: Any) -> RelayMessage:
        """Send a chat message, routing through the scheduler if configured."""
        if self._scheduler is not None:
            try:
                return self._scheduler.send(message, **metadata)
            except Exception as exc:
                logger.error(f"Scheduler send failed, falling back to direct: {exc}")
        return self.relay.post_message(self.identity, message, metadata=metadata)

    # ── Polling ───────────────────────────────────────────────────

    def _poll_loop(self) -> None:
        """Background polling loop (daemon thread)."""
        while self._running:
            try:
                self._poll_once()
            except Exception as exc:
                logger.error(f"RelayEndpoint poll error: {exc}")
            time.sleep(self.poll_interval)

    def _poll_once(self) -> None:
        """Single poll iteration: read new messages and dispatch."""
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
            elif msg.msg_type == MSG_SYSTEM:
                logger.info(f"[system] {msg.content}")

    # ── Message Handling ──────────────────────────────────────────

    def _handle_chat(self, msg: RelayMessage) -> None:
        """Try custom handlers first, then auto-respond via LLM."""
        logger.info(f"[{msg.sender}] {msg.content[:100]}")
        for handler in self._on_message:
            try:
                response = handler(msg)
                if response:
                    self.relay.post_message(self.identity, response)
                    return
            except Exception as exc:
                logger.error(f"Message handler error: {exc}")
        if self.auto_respond:
            self._auto_respond(msg)

    def _auto_respond(self, msg: RelayMessage) -> None:
        """Generate and post an LLM response."""
        try:
            request = AgentRequest(prompt=msg.content, metadata=msg.metadata)
            response = self.client.execute_with_session(
                request, session=self.session,
            )
            if response.is_success():
                self.relay.post_message(
                    self.identity,
                    response.content,
                    metadata={
                        "tokens_used": getattr(response, "tokens_used", 0),
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
        except Exception as exc:
            logger.error(f"Auto-respond failed: {exc}")
            self.relay.post_message(
                self.identity,
                f"[error] Failed to generate response: {exc}",
                metadata={"error": True, "in_reply_to": msg.id},
            )

    def _handle_tool_request(self, msg: RelayMessage) -> None:
        """Execute a tool request via the MCP bridge."""
        try:
            from codomyrmex.agents.pai.mcp_bridge import call_tool
            result = call_tool(msg.tool_name, **(msg.tool_args or {}))
            self.relay.post_tool_result(self.identity, msg.id, result)
        except Exception as exc:
            logger.error(f"Tool request failed: {exc}")
            self.relay.post_tool_result(
                self.identity, msg.id, None, error=str(exc),
            )


__all__ = ["RelayEndpoint"]
