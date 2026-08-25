"""Autonomous Agent Implementation.

Provides a long-lived, autonomous agent class that can execute in a loop,
respond to messages on a relay channel, and maintain a persona.
"""

import time

from codomyrmex.agents.llm_client import AgentRequest, get_llm_client
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def _make_endpoint(
    channel: str,
    identity: str,
    poll_interval: float,
    client: object,
    scheduler_config: object | None,
) -> object:
    """Create the provider-agnostic relay endpoint."""
    from codomyrmex.ide.antigravity.relay_endpoint import RelayEndpoint

    return RelayEndpoint(
        channel,
        llm_client=client,
        identity=identity,
        poll_interval=poll_interval,
        auto_respond=False,
        scheduler_config=scheduler_config,
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
        self.identity = identity
        self.persona = persona
        self.channel = channel
        self.poll_interval = poll_interval
        self.think_time = think_time
        self.running = False
        self._scheduler_config = scheduler_config

        self.client = get_llm_client(identity)

        self.endpoint = _make_endpoint(
            channel,
            identity,
            poll_interval,
            self.client,
            scheduler_config,
        )

        self.endpoint.on_message(self._handle_message)

        # If scheduler is available on the endpoint, expose it
        self._scheduler = getattr(self.endpoint, "_scheduler", None)

    def start(self, background: bool = True) -> None:
        """Start the agent loop."""
        logger.info("[%s] Starting Autonomous Agent (%s)", self.identity, self.persona)
        try:
            self.endpoint.start()
        except Exception:
            # A failed endpoint start must not leave the public lifecycle
            # flag claiming that the agent is running.
            self.running = False
            raise
        self.running = True

        if not background:
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()

    def stop(self) -> None:
        """Stop the agent loop."""
        logger.info("[%s] Stopping...", self.identity)
        try:
            self.endpoint.stop()
        except Exception:
            # Preserve the observable running state until shutdown actually
            # succeeds; callers can retry or surface the failure.
            self.running = True
            raise
        self.running = False

    def send(self, message: str) -> None:
        """Send a message to the channel."""
        logger.info("[%s] Sending: %s...", self.identity, message[:50])
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

        logger.info(
            "[%s] Received from %s: %s...", self.identity, msg.sender, msg.content[:50]
        )

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

            if hasattr(resp, "is_success") and not resp.is_success():
                raise RuntimeError(resp.error or "provider returned a failure")

            reply = resp.content.strip()
            if not reply:
                raise RuntimeError("provider returned an empty response")
            self.send(reply)

            # CHECKPOINT PRODUCER SITE:
            # Uncomment the following to save a checkpoint after each response.
            # See agents/transport/checkpoint.py for the full producer snippet.
            #
            # from codomyrmex.agents.transport.checkpoint import Checkpoint
            # from codomyrmex.agents.transport.serializer import AgentSerializer
            # serializer = AgentSerializer()
            # snapshot = serializer.snapshot(
            #     agent_id=self.identity,
            #     agent_type="AutonomousAgent",
            #     config={"persona": self.persona, "channel": self.channel},
            #     memory={"last_reply": reply},
            # )
            # ckpt = Checkpoint(snapshot=snapshot)
            # ckpt.save(f"/tmp/codomyrmex-{self.identity}-checkpoint.json")

            if self._scheduler is not None:
                self._scheduler.record_success()

        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("[%s] Generation error: %s", self.identity, e)
            if self._scheduler is not None:
                self._scheduler.record_error()


__all__ = [
    "AutonomousAgent",
]
