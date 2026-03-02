"""Token-bucket rate limiter for MCP server.

Prevents individual tools or clients from consuming disproportionate
resources, enforcing per-tool and global request ceilings.

Usage::

    limiter = RateLimiter(rate=10, burst=20)   # 10 req/s, burst of 20
    if limiter.allow("codomyrmex.read_file"):
        ...  # proceed
    else:
        ...  # reject / queue

The limiter uses the **token bucket** algorithm:
- Tokens refill at ``rate`` tokens per second.
- The bucket holds up to ``burst`` tokens.
- Each request consumes one token.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


# ── Configuration ────────────────────────────────────────────────────

@dataclass
class RateLimiterConfig:
    """Rate limiter tuning parameters.

    Attributes:
        rate: Tokens added per second (sustained rate).
        burst: Maximum tokens in the bucket (peak burst).
        per_tool_rate: Optional per-tool rate override map.
        per_tool_burst: Optional per-tool burst override map.
    """
    rate: float = 50.0
    burst: int = 100
    per_tool_rate: dict[str, float] = field(default_factory=dict)
    per_tool_burst: dict[str, int] = field(default_factory=dict)


# ── Token bucket ─────────────────────────────────────────────────────

class _TokenBucket:
    """Single token bucket."""

    __slots__ = ("rate", "burst", "_tokens", "_last_refill")

    def __init__(self, rate: float, burst: int) -> None:
        """Initialize this instance."""
        self.rate = rate
        self.burst = burst
        self._tokens = float(burst)
        self._last_refill = time.monotonic()

    def _refill(self) -> None:
        """refill ."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.burst, self._tokens + elapsed * self.rate)
        self._last_refill = now

    def consume(self, n: int = 1) -> bool:
        """Try to consume *n* tokens.  Returns True on success."""
        self._refill()
        if self._tokens >= n:
            self._tokens -= n
            return True
        return False

    @property
    def tokens(self) -> float:
        """tokens ."""
        self._refill()
        return self._tokens

    @property
    def metrics(self) -> dict[str, Any]:
        """metrics ."""
        return {
            "tokens": round(self.tokens, 2),
            "rate": self.rate,
            "burst": self.burst,
        }


# ── Rate limiter ─────────────────────────────────────────────────────

class RateLimiter:
    """Token-bucket rate limiter with per-tool overrides.

    Args:
        config: Limiter configuration (defaults: 50 req/s, burst 100).
    """

    def __init__(self, config: RateLimiterConfig | None = None) -> None:
        """Initialize this instance."""
        self.config = config or RateLimiterConfig()
        self._global = _TokenBucket(self.config.rate, self.config.burst)
        self._per_tool: dict[str, _TokenBucket] = {}

    def _get_tool_bucket(self, tool_name: str) -> _TokenBucket | None:
        """Return per-tool bucket if configured, creating lazily."""
        if tool_name in self._per_tool:
            return self._per_tool[tool_name]
        rate = self.config.per_tool_rate.get(tool_name)
        burst = self.config.per_tool_burst.get(tool_name)
        if rate is not None or burst is not None:
            bucket = _TokenBucket(
                rate or self.config.rate,
                burst or self.config.burst,
            )
            self._per_tool[tool_name] = bucket
            return bucket
        return None

    def allow(self, tool_name: str = "") -> bool:
        """Check if a request for *tool_name* is allowed.

        Consumes one global token and (if configured) one per-tool token.
        Returns False if either bucket is exhausted.
        """
        # Per-tool check first (don't consume global token if tool is limited)
        tool_bucket = self._get_tool_bucket(tool_name) if tool_name else None
        if tool_bucket and not tool_bucket.consume():
            logger.warning("Rate limit hit for tool %s", tool_name)
            return False
        # Global check
        if not self._global.consume():
            logger.warning("Global rate limit hit (tool=%s)", tool_name)
            return False
        return True

    @property
    def metrics(self) -> dict[str, Any]:
        """Return current rate limiter metrics."""
        result: dict[str, Any] = {"global": self._global.metrics}
        if self._per_tool:
            result["per_tool"] = {
                name: bucket.metrics for name, bucket in self._per_tool.items()
            }
        return result

    def reset(self) -> None:
        """Reset all buckets to full."""
        self._global = _TokenBucket(self.config.rate, self.config.burst)
        self._per_tool.clear()
