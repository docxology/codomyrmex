"""Autonomous Agent Implementation.

Provides a long-lived, autonomous agent class that can execute in a loop,
respond to messages on a relay channel, and maintain a persona.
"""

import logging
import time

from codomyrmex.agents.llm_client import AgentRequest, get_llm_client

logger = logging.getLogger(__name__)


def _make_endpoint(
    channel: str,
    identity: str,
    poll_interval: float,
    client: object,
    scheduler_config: object | None,
) -> object:
    """Create the best available relay endpoint.

    Prefers :class:`RelayEndpoint` (provider-agnostic); falls back to
    the :class:`ClaudeCodeEndpoint` interface.
    """
    try:
        from codomyrmex.ide.antigravity.relay_endpoint import RelayEndpoint
        return RelayEndpoint(
            channel,
            llm_client=client,
            identity=identity,
            poll_interval=poll_interval,
            auto_respond=False,
            scheduler_config=scheduler_config,
        )
    except ImportError:
        from codomyrmex.ide.antigravity.live_bridge import ClaudeCodeEndpoint
        return ClaudeCodeEndpoint(
            channel,
            claude_client=client,
            identity=identity,
            poll_interval=poll_interval,
            auto_respond=False,
        )


class AutonomousAgent:
    """A long-lived autonomous agent connected to a Relay Channel.

    Attributes:
        identity: The agent's name/ID on the channel.
        persona: Description of the agent's role/personality.
        channel: The relay channel ID to connect to.
        poll_interval: How often to check for messages (seconds).
        think_time: Artificial delay before responding (seconds).
        scheduler_config: Optional :class:`SchedulerConfig` for rate-limited
            sending.  When provided, the scheduler's computed delay replaces
            the raw ``think_time`` sleep.
    """

    def __init__(
        self,
        identity: str,
        persona: str,
        channel: str,
        poll_interval: float = 1.0,
        think_time: float = 2.0,
        model: str | None = None,
        scheduler_config: object | None = None,
    ):
        """Initialize this instance."""
        self.identity = identity
        self.persona = persona
        self.channel = channel
        self.poll_interval = poll_interval
        self.think_time = think_time
        self.running = False
        self._scheduler_config = scheduler_config

        # Initialize Client
        self.client = get_llm_client(identity)

        # Initialize Endpoint (provider-agnostic relay wrapper)
        self.endpoint = _make_endpoint(
            channel, identity, poll_interval, self.client, scheduler_config,
        )

        self.endpoint.on_message(self._handle_message)

        # If scheduler is available on the endpoint, expose it
        self._scheduler = getattr(self.endpoint, "_scheduler", None)

    def start(self, background: bool = True) -> None:
        """Start the agent loop."""
        logger.info(f"[{self.identity}] Starting Autonomous Agent ({self.persona})")
        self.running = True
        self.endpoint.start()

        if not background:
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()

    def stop(self) -> None:
        """Stop the agent loop."""
        logger.info(f"[{self.identity}] Stopping...")
        self.running = False
        self.endpoint.stop()

    def send(self, message: str) -> None:
        """Send a message to the channel."""
        logger.info(f"[{self.identity}] Sending: {message[:50]}...")
        self.endpoint.relay.post_message(self.identity, message)

    def pause(self) -> None:
        """Pause message sending (delegates to scheduler if available)."""
        if self._scheduler is not None:
            self._scheduler.pause()

    def resume(self) -> None:
        """Resume message sending (delegates to scheduler if available)."""
        if self._scheduler is not None:
            self._scheduler.resume()

    def _handle_message(self, msg) -> None:
        """Handle incoming messages."""
        if not self.running:
            return

        if msg.sender == self.identity:
            return

        if not msg.is_chat:
            return

        logger.info(f"[{self.identity}] Received from {msg.sender}: {msg.content[:50]}...")

        if not self.running:
            return

        # Generate Reply
        try:
            prompt = (
                f"System: You are {self.identity}. Persona: {self.persona}.\n"
                f"Reflect on the message and provide a thoughtful response.\n"
                f"User: {msg.content}"
            )
            req = AgentRequest(prompt=prompt)
            resp = self.client.execute_with_session(req)

            reply = resp.content.strip()
            self.send(reply)

            if self._scheduler is not None:
                self._scheduler.record_success()

        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error(f"[{self.identity}] Generation error: {e}")
            if self._scheduler is not None:
                self._scheduler.record_error()
