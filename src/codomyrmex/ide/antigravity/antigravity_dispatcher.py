"""Antigravity Dispatcher -- bridge relay messages INTO Antigravity's chat UI.

Polls an :class:`AgentRelay` channel for messages from non-Antigravity senders
and forwards each one to the Antigravity IDE via either the CLI
(``send_chat_message``) or GUI automation (``send_chat_gui``).

Example::

    >>> from codomyrmex.ide.antigravity.agent_relay import AgentRelay
    >>> from codomyrmex.ide.antigravity.antigravity_dispatcher import (
    ...     AntigravityDispatcher, DispatcherConfig,
    ... )
    >>> relay = AgentRelay("collab-session")
    >>> dispatcher = AntigravityDispatcher(relay)
    >>> dispatcher.start()
    >>> # ... messages arriving on the relay are forwarded to Antigravity ...
    >>> dispatcher.stop()
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
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
)


# =====================================================================
# Configuration
# =====================================================================

@dataclass
class DispatcherConfig:
    """Configuration for :class:`AntigravityDispatcher`.

    Attributes:
        relay_to_ag: Channel name for relay-to-Antigravity messages.
        ag_to_relay: Channel name reserved for Antigravity-to-relay
            messages (currently unused).
        use_gui: If ``True`` forward messages via AppleScript GUI
            automation; if ``False`` (default) use the CLI path.
        response_timeout: Maximum seconds to wait for a forwarding
            acknowledgement (reserved for future use).
        response_poll_interval: Seconds between relay polls.
        sender_filter: When set, only forward messages whose
            ``sender`` matches this value.  ``None`` means forward
            messages from **all** non-Antigravity senders.
    """

    relay_to_ag: str = "relay_to_ag"
    ag_to_relay: str = "ag_to_relay"
    use_gui: bool = False
    response_timeout: float = 60.0
    response_poll_interval: float = 2.0
    sender_filter: str | None = None


# =====================================================================
# Dispatcher
# =====================================================================

class AntigravityDispatcher:
    """Forward relay messages into Antigravity's real chat UI.

    The dispatcher runs a daemon thread that continuously polls the
    relay for new messages, filters out those originating from
    ``"antigravity"`` (to prevent echo loops), and dispatches the rest
    to the Antigravity IDE via the configured transport (CLI or GUI).

    Attributes:
        relay: The :class:`AgentRelay` instance being polled.
        config: Dispatcher configuration.
    """

    def __init__(
        self,
        relay: AgentRelay,
        *,
        client: Any | None = None,
        scheduler: Any | None = None,
        config: DispatcherConfig | None = None,
    ) -> None:
        """Initialize the dispatcher.

        Args:
            relay: Relay channel to poll for inbound messages.
            client: An ``AntigravityClient`` instance.  If ``None`` one
                is lazily created on first dispatch.
            scheduler: An optional ``MessageScheduler`` used to record
                forwarding outcomes (``record_success`` /
                ``record_error``).
            config: Dispatcher tunables.  Defaults are used when
                ``None``.
        """
        self.relay = relay
        self.config = config or DispatcherConfig()

        self._client = client
        self._scheduler = scheduler

        # Polling state
        self._cursor: int = 0
        self._running: bool = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

        # Statistics
        self._forwarded_count: int = 0
        self._failed_count: int = 0
        self._last_forwarded_at: str | None = None

    # ── Lifecycle ─────────────────────────────────────────────────

    def start(self) -> None:
        """Start the background polling thread.

        The thread is marked as a daemon so it will not prevent the
        interpreter from exiting.  Calling ``start`` on an
        already-running dispatcher is a no-op.
        """
        if self._running:
            logger.warning("AntigravityDispatcher is already running")
            return

        self._cursor = self.relay.get_latest_cursor()
        self._running = True

        self._thread = threading.Thread(
            target=self._poll_loop,
            name="ag-dispatcher",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            "AntigravityDispatcher started on channel %s (gui=%s)",
            self.relay.channel_id,
            self.config.use_gui,
        )

    def stop(self) -> None:
        """Stop the background thread and wait for it to finish."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=self.config.response_poll_interval * 3)
            self._thread = None
        logger.info("AntigravityDispatcher stopped")

    @property
    def is_running(self) -> bool:
        """Whether the polling thread is active."""
        return self._running

    # ── Public API ────────────────────────────────────────────────

    def forward_to_antigravity(self, msg: RelayMessage) -> bool:
        """Manually forward a single message to Antigravity.

        This bypasses the polling loop and sender filter, immediately
        dispatching *msg* to the configured transport.

        Args:
            msg: The relay message to forward.

        Returns:
            ``True`` if the message was forwarded successfully.
        """
        return self._dispatch_to_ag(msg)

    def get_stats(self) -> dict[str, Any]:
        """Return forwarding statistics.

        Returns:
            Dictionary with ``forwarded_count``, ``failed_count``,
            ``last_forwarded_at``, and ``running`` keys.
        """
        return {
            "forwarded_count": self._forwarded_count,
            "failed_count": self._failed_count,
            "last_forwarded_at": self._last_forwarded_at,
            "running": self._running,
        }

    # ── Polling internals ─────────────────────────────────────────

    def _poll_loop(self) -> None:
        """Background loop: poll, filter, dispatch.  Runs until
        ``_running`` is set to ``False``."""
        while self._running:
            try:
                self._poll_once()
            except Exception:
                logger.exception("AntigravityDispatcher poll error")
            time.sleep(self.config.response_poll_interval)

    def _poll_once(self) -> None:
        """Execute a single poll-filter-dispatch cycle."""
        messages = self.relay.poll_messages(since_cursor=self._cursor)

        for msg in messages:
            self._cursor = max(self._cursor, msg.cursor)

            # Never echo Antigravity's own messages back to itself.
            if msg.sender == "antigravity":
                continue

            # Honour the optional sender filter.
            if (
                self.config.sender_filter is not None
                and msg.sender != self.config.sender_filter
            ):
                continue

            self._dispatch_to_ag(msg)

    # ── Dispatch ──────────────────────────────────────────────────

    def _dispatch_to_ag(self, msg: RelayMessage) -> bool:
        """Forward *msg* to Antigravity via the configured transport.

        If a ``scheduler`` was provided, its ``record_success`` or
        ``record_error`` method is called after the attempt.

        Args:
            msg: Relay message to forward.

        Returns:
            ``True`` on success, ``False`` on failure.
        """
        # Lazy-initialise the client if none was injected.
        if self._client is None:
            try:
                from codomyrmex.ide.antigravity import AntigravityClient
                self._client = AntigravityClient()
            except Exception:
                logger.exception("Failed to create AntigravityClient")
                self._failed_count += 1
                if self._scheduler is not None:
                    try:
                        self._scheduler.record_error()
                    except Exception:
                        logger.exception("Scheduler record_error failed")
                return False

        try:
            if self.config.use_gui:
                result = self._client.send_chat_gui(msg.content)
            else:
                result = self._client.send_chat_message(msg.content)

            success = getattr(result, "success", bool(result))

            if success:
                with self._lock:
                    self._forwarded_count += 1
                    self._last_forwarded_at = datetime.now(timezone.utc).isoformat()
                logger.info(
                    "Forwarded message %s from %s to Antigravity",
                    msg.id,
                    msg.sender,
                )
                if self._scheduler is not None:
                    try:
                        self._scheduler.record_success()
                    except Exception:
                        logger.exception("Scheduler record_success failed")
                return True
            else:
                error_detail = getattr(result, "error", "unknown error")
                logger.error(
                    "Antigravity rejected message %s: %s",
                    msg.id,
                    error_detail,
                )
                with self._lock:
                    self._failed_count += 1
                if self._scheduler is not None:
                    try:
                        self._scheduler.record_error()
                    except Exception:
                        logger.exception("Scheduler record_error failed")
                return False

        except Exception:
            logger.exception(
                "Exception dispatching message %s to Antigravity", msg.id,
            )
            with self._lock:
                self._failed_count += 1
            if self._scheduler is not None:
                try:
                    self._scheduler.record_error()
                except Exception:
                    logger.exception("Scheduler record_error failed")
            return False


__all__ = ["AntigravityDispatcher", "DispatcherConfig"]
