"""Message Scheduler --- Rate-limited, delay-aware message scheduling for AgentRelay.

Wraps an :class:`AgentRelay` instance with sliding-window rate limiting,
exponential backoff on consecutive errors, and pause/resume control.  All
public send methods block the calling thread for the computed delay before
actually appending to the relay, making this suitable for polite,
throttled agent-to-agent communication.

Example::

    >>> from codomyrmex.ide.antigravity.agent_relay import AgentRelay
    >>> from codomyrmex.ide.antigravity.message_scheduler import (
    ...     MessageScheduler, SchedulerConfig,
    ... )
    >>> relay = AgentRelay("my-channel")
    >>> scheduler = MessageScheduler(relay, SchedulerConfig(min_delay=0.5))
    >>> msg = scheduler.send("Hello from scheduler")
    >>> scheduler.get_stats()
    {'send_count': 1, 'error_count': 0, 'paused': False, 'avg_delay': ...}
"""

from __future__ import annotations

import random
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any

from codomyrmex.ide.antigravity.agent_relay import AgentRelay, RelayMessage

try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

__all__ = ["MessageScheduler", "SchedulerConfig"]

# One hour in seconds -- used as the sliding-window size for rate limiting.
_HOUR_SECONDS: float = 3600.0


# =====================================================================
# Configuration
# =====================================================================

@dataclass
class SchedulerConfig:
    """Tuning knobs for :class:`MessageScheduler`.

    Attributes:
        min_delay: Minimum random delay (seconds) injected before each send.
        max_delay: Maximum random delay (seconds) injected before each send.
        max_messages_per_hour: Sliding-window rate limit.
        backoff_base: Base delay added when consecutive errors > 0.
        backoff_max: Upper cap on exponential backoff delay.
        backoff_factor: Multiplier applied per consecutive error.
    """

    min_delay: float = 1.0
    max_delay: float = 5.0
    max_messages_per_hour: int = 120
    backoff_base: float = 1.0
    backoff_max: float = 30.0
    backoff_factor: float = 2.0


# =====================================================================
# Scheduler
# =====================================================================

class MessageScheduler:
    """Rate-limited wrapper around :class:`AgentRelay`.

    Every call to :meth:`send` or :meth:`send_tool_request` will:

    1. Block while the scheduler is paused.
    2. Compute a jittered delay (plus exponential backoff if errors exist).
    3. Sleep for the computed delay.
    4. Enforce the sliding-window rate limit (sleep more if needed).
    5. Delegate to the underlying relay and record the send timestamp.

    Thread safety is provided by a :class:`threading.Lock` guarding all
    mutations to the internal send-time deque.
    """

    def __init__(
        self,
        relay: AgentRelay,
        config: SchedulerConfig | None = None,
        *,
        identity: str = "scheduler",
    ) -> None:
        """Execute   Init   operations natively."""
        self._relay = relay
        self._config = config or SchedulerConfig()
        self._identity = identity

        # Sliding-window of send timestamps (epoch floats).
        self._send_times: deque[float] = deque()
        self._lock = threading.Lock()

        # Backoff state.
        self._consecutive_errors: int = 0

        # Pause control -- *set* means running, *clear* means paused.
        self._paused = threading.Event()
        self._paused.set()

        # Bookkeeping for stats.
        self._total_sends: int = 0
        self._total_errors: int = 0
        self._total_delay: float = 0.0

        logger.info(
            "MessageScheduler ready  identity=%s  channel=%s  rate=%d/h",
            self._identity,
            self._relay.channel_id,
            self._config.max_messages_per_hour,
        )

    # ── Public API ────────────────────────────────────────────────

    def send(self, content: str, **metadata: Any) -> RelayMessage:
        """Send a rate-limited chat message through the relay.

        Args:
            content: Message text.
            **metadata: Arbitrary key/value pairs forwarded as message metadata.

        Returns:
            The :class:`RelayMessage` appended to the relay.
        """
        msg = RelayMessage(
            sender=self._identity,
            msg_type="chat",
            content=content,
            metadata=metadata if metadata else {},
        )
        return self._wait_and_send(msg)

    def send_tool_request(
        self,
        tool_name: str,
        tool_args: dict[str, Any] | None = None,
    ) -> RelayMessage:
        """Send a rate-limited tool request through the relay.

        Args:
            tool_name: Name of the tool to invoke.
            tool_args: Optional arguments for the tool.

        Returns:
            The :class:`RelayMessage` appended to the relay.
        """
        msg = RelayMessage(
            sender=self._identity,
            msg_type="tool_request",
            content=f"Execute tool: {tool_name}",
            tool_name=tool_name,
            tool_args=tool_args or {},
        )
        return self._wait_and_send(msg)

    def record_error(self) -> None:
        """Increment the consecutive-error counter (increases backoff)."""
        self._consecutive_errors += 1
        self._total_errors += 1
        logger.warning(
            "Scheduler error recorded  consecutive=%d  total=%d",
            self._consecutive_errors,
            self._total_errors,
        )

    def record_success(self) -> None:
        """Reset the consecutive-error counter (clears backoff)."""
        if self._consecutive_errors > 0:
            logger.info(
                "Scheduler backoff reset  was=%d", self._consecutive_errors,
            )
        self._consecutive_errors = 0

    def pause(self) -> None:
        """Pause all message sending.  Calls to *send* will block until resumed."""
        self._paused.clear()
        logger.info("Scheduler paused")

    def resume(self) -> None:
        """Resume message sending."""
        self._paused.set()
        logger.info("Scheduler resumed")

    def get_stats(self) -> dict[str, Any]:
        """Return scheduler statistics.

        Returns:
            Dictionary with ``send_count``, ``error_count``, ``paused``,
            and ``avg_delay``.
        """
        avg = (self._total_delay / self._total_sends) if self._total_sends else 0.0
        return {
            "send_count": self._total_sends,
            "error_count": self._total_errors,
            "paused": not self._paused.is_set(),
            "avg_delay": round(avg, 4),
        }

    # ── Internals ─────────────────────────────────────────────────

    def _compute_delay(self) -> float:
        """Compute the next delay: random jitter + exponential backoff."""
        jitter = random.uniform(self._config.min_delay, self._config.max_delay)
        if self._consecutive_errors > 0:
            backoff = min(
                self._config.backoff_base
                * self._config.backoff_factor ** self._consecutive_errors,
                self._config.backoff_max,
            )
        else:
            backoff = 0.0
        return jitter + backoff

    def _check_rate_limit(self) -> float:
        """Return seconds to wait if the sliding-window limit is exceeded, else 0."""
        now = time.monotonic()
        with self._lock:
            # Prune timestamps older than one hour.
            while self._send_times and (now - self._send_times[0]) > _HOUR_SECONDS:
                self._send_times.popleft()

            if len(self._send_times) >= self._config.max_messages_per_hour:
                # Must wait until the oldest entry expires from the window.
                wait = _HOUR_SECONDS - (now - self._send_times[0])
                return max(wait, 0.0)
        return 0.0

    def _wait_and_send(self, msg: RelayMessage) -> RelayMessage:
        """Core send path: pause gate -> delay -> rate limit -> relay append."""
        # 1. Block while paused.
        self._paused.wait()

        # 2. Jitter + backoff delay.
        delay = self._compute_delay()
        if delay > 0:
            logger.debug("Scheduler sleeping %.2fs  (errors=%d)", delay, self._consecutive_errors)
            time.sleep(delay)

        # 3. Sliding-window rate limit.
        rate_wait = self._check_rate_limit()
        if rate_wait > 0:
            logger.info("Rate limit hit  waiting %.1fs", rate_wait)
            time.sleep(rate_wait)

        # 4. Append to relay and record timestamp.
        self._relay._append(msg)

        now = time.monotonic()
        with self._lock:
            self._send_times.append(now)

        self._total_sends += 1
        self._total_delay += delay + rate_wait

        logger.debug(
            "Scheduled message sent  id=%s  type=%s  delay=%.2f",
            msg.id,
            msg.msg_type,
            delay + rate_wait,
        )
        return msg
