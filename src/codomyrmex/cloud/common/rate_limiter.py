"""Token-bucket rate limiter for cloud provider API calls.

Provides per-provider rate limiting with configurable burst capacity,
automatic retry-after handling, and thread-safe token acquisition.

Example::

    config = RateLimiterConfig(max_requests_per_second=10.0, burst_size=20)
    limiter = TokenBucketLimiter(config)

    # Block until a token is available
    limiter.wait()
    response = make_api_call()

    # Non-blocking check
    if limiter.try_acquire():
        response = make_api_call()


    # Decorator-style usage
    @rate_limited(limiter)
    def call_provider():
        return make_api_call()
"""

from __future__ import annotations

import functools
import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


@dataclass(frozen=True)
class RateLimiterConfig:
    """Configuration for a token-bucket rate limiter.

    Attributes:
        max_requests_per_second: Sustained request rate.
        burst_size: Maximum tokens that can accumulate for burst traffic.
        retry_after_seconds: Default back-off when rate-limited by the server.
        provider_name: Human-readable provider label for logging.
    """

    max_requests_per_second: float = 10.0
    burst_size: int = 20
    retry_after_seconds: float = 1.0
    provider_name: str = "unknown"


class TokenBucketLimiter:
    """Thread-safe token-bucket rate limiter.

    Tokens refill at ``config.max_requests_per_second`` up to
    ``config.burst_size``.  Calling :meth:`wait` blocks until a token
    is available; :meth:`try_acquire` is non-blocking.

    Args:
        config: Rate limiter configuration.

    Example::

        limiter = TokenBucketLimiter(RateLimiterConfig(max_requests_per_second=5))
        limiter.wait()
        do_work()
    """

    def __init__(self, config: RateLimiterConfig) -> None:
        self._config = config
        self._tokens: float = float(config.burst_size)
        self._last_refill: float = time.monotonic()
        self._lock = threading.Lock()
        self._total_acquired: int = 0
        self._total_waited_seconds: float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def config(self) -> RateLimiterConfig:
        """Return the limiter configuration."""
        return self._config

    @property
    def remaining_tokens(self) -> float:
        """Return current token count (after refill)."""
        with self._lock:
            self._refill()
            return self._tokens

    @property
    def total_acquired(self) -> int:
        """Total tokens successfully acquired since creation."""
        return self._total_acquired

    @property
    def total_waited_seconds(self) -> float:
        """Cumulative seconds spent waiting for tokens."""
        return self._total_waited_seconds

    def try_acquire(self, tokens: int = 1) -> bool:
        """Try to acquire *tokens* without blocking.

        Args:
            tokens: Number of tokens to consume.

        Returns:
            ``True`` if tokens were acquired, ``False`` otherwise.
        """
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                self._total_acquired += tokens
                return True
            return False

    def wait(self, tokens: int = 1, timeout: float | None = None) -> bool:
        """Block until *tokens* are available.

        Args:
            tokens: Number of tokens to consume.
            timeout: Maximum seconds to wait (``None`` = unlimited).

        Returns:
            ``True`` if tokens were acquired within the timeout.

        Raises:
            ValueError: If *tokens* exceeds the burst size.
        """
        if tokens > self._config.burst_size:
            msg = (
                f"Requested {tokens} tokens but burst_size is {self._config.burst_size}"
            )
            raise ValueError(msg)

        deadline = time.monotonic() + timeout if timeout is not None else None
        waited = 0.0

        while True:
            with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    self._total_acquired += tokens
                    self._total_waited_seconds += waited
                    return True

                # Calculate how long until enough tokens are available
                deficit = tokens - self._tokens
                sleep_time = deficit / self._config.max_requests_per_second

            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                sleep_time = min(sleep_time, remaining)

            time.sleep(sleep_time)
            waited += sleep_time

    def handle_retry_after(self, retry_after: float | None = None) -> None:
        """Pause the limiter after receiving a server-side rate-limit response.

        Args:
            retry_after: Seconds to wait (falls back to config default).
        """
        pause = retry_after or self._config.retry_after_seconds
        logger.warning(
            "Rate-limited by %s — backing off %.1fs",
            self._config.provider_name,
            pause,
        )
        time.sleep(pause)
        # Drain tokens to prevent immediate burst after back-off
        with self._lock:
            self._tokens = 0.0
            self._last_refill = time.monotonic()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _refill(self) -> None:
        """Refill tokens based on elapsed time (must be called under lock)."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        new_tokens = elapsed * self._config.max_requests_per_second
        self._tokens = min(self._tokens + new_tokens, float(self._config.burst_size))
        self._last_refill = now


def rate_limited(limiter: TokenBucketLimiter) -> Callable[[F], F]:
    """Decorator that acquires a rate-limit token before each call.

    Args:
        limiter: The :class:`TokenBucketLimiter` to use.

    Returns:
        Decorated callable.

    Example::

        limiter = TokenBucketLimiter(RateLimiterConfig(max_requests_per_second=5))


        @rate_limited(limiter)
        def call_api(): ...
    """

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            limiter.wait()
            return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


# ------------------------------------------------------------------
# Registry for per-provider limiters
# ------------------------------------------------------------------

_provider_limiters: dict[str, TokenBucketLimiter] = {}
_registry_lock = threading.Lock()


def get_provider_limiter(
    provider_name: str,
    config: RateLimiterConfig | None = None,
) -> TokenBucketLimiter:
    """Get or create a rate limiter for *provider_name*.

    Args:
        provider_name: Unique provider key (e.g. ``"aws"``, ``"openai"``).
        config: Optional config; a sensible default is used if omitted.

    Returns:
        The :class:`TokenBucketLimiter` registered for this provider.
    """
    with _registry_lock:
        if provider_name not in _provider_limiters:
            cfg = config or RateLimiterConfig(provider_name=provider_name)
            _provider_limiters[provider_name] = TokenBucketLimiter(cfg)
        return _provider_limiters[provider_name]


def reset_all_limiters() -> None:
    """Remove all registered provider limiters (useful for testing)."""
    with _registry_lock:
        _provider_limiters.clear()


__all__ = [
    "RateLimiterConfig",
    "TokenBucketLimiter",
    "get_provider_limiter",
    "rate_limited",
    "reset_all_limiters",
]
