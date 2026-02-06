"""Comprehensive tests for the codomyrmex.api.rate_limiting module.

Tests cover all public API surface: RateLimitResult, FixedWindowLimiter,
SlidingWindowLimiter, TokenBucketLimiter, CompositeRateLimiter,
RateLimiterMiddleware, and the create_rate_limiter factory.
"""

import time
from datetime import datetime, timedelta

import pytest

from codomyrmex.api.rate_limiting import (
    CompositeRateLimiter,
    FixedWindowLimiter,
    RateLimiterMiddleware,
    RateLimitResult,
    SlidingWindowLimiter,
    TokenBucketLimiter,
    create_rate_limiter,
)

# ---------------------------------------------------------------------------
# RateLimitResult
# ---------------------------------------------------------------------------

class TestRateLimitResult:
    """Tests for the RateLimitResult dataclass."""

    def test_field_defaults(self):
        """retry_after should default to None when not provided."""
        reset = datetime.now() + timedelta(seconds=60)
        result = RateLimitResult(allowed=True, limit=100, remaining=99, reset_at=reset)

        assert result.allowed is True
        assert result.limit == 100
        assert result.remaining == 99
        assert result.reset_at == reset
        assert result.retry_after is None

    def test_to_headers_without_retry_after(self):
        """Headers should include Limit, Remaining, Reset but not Retry-After."""
        reset = datetime(2026, 1, 1, 0, 0, 0)
        result = RateLimitResult(allowed=True, limit=50, remaining=49, reset_at=reset)

        headers = result.to_headers()
        assert headers["X-RateLimit-Limit"] == "50"
        assert headers["X-RateLimit-Remaining"] == "49"
        assert "X-RateLimit-Reset" in headers
        assert "Retry-After" not in headers

    def test_to_headers_with_retry_after(self):
        """When retry_after is set, Retry-After header should be present."""
        reset = datetime(2026, 1, 1, 0, 0, 0)
        result = RateLimitResult(
            allowed=False, limit=10, remaining=0, reset_at=reset, retry_after=30.7
        )

        headers = result.to_headers()
        assert headers["Retry-After"] == "30"
        assert headers["X-RateLimit-Remaining"] == "0"


# ---------------------------------------------------------------------------
# FixedWindowLimiter
# ---------------------------------------------------------------------------

class TestFixedWindowLimiter:
    """Tests for the FixedWindowLimiter."""

    def test_consume_within_limit(self):
        """Requests within the limit should be allowed."""
        limiter = FixedWindowLimiter(limit=5, window_seconds=60)

        for i in range(5):
            result = limiter.consume("user:1")
            assert result.allowed is True
            assert result.remaining == 5 - (i + 1)

    def test_rate_limit_after_threshold(self):
        """Exceeding the limit should deny subsequent requests."""
        limiter = FixedWindowLimiter(limit=3, window_seconds=60)

        for _ in range(3):
            result = limiter.consume("user:1")
            assert result.allowed is True

        denied = limiter.consume("user:1")
        assert denied.allowed is False
        assert denied.remaining == 0
        assert denied.retry_after is not None
        assert denied.retry_after > 0

    def test_separate_keys_are_independent(self):
        """Different keys should have independent limits."""
        limiter = FixedWindowLimiter(limit=2, window_seconds=60)

        limiter.consume("user:1")
        limiter.consume("user:1")

        result = limiter.consume("user:2")
        assert result.allowed is True
        assert result.remaining == 1

    def test_check_without_consuming(self):
        """check() should not consume any tokens."""
        limiter = FixedWindowLimiter(limit=3, window_seconds=60)

        limiter.consume("user:1")

        check1 = limiter.check("user:1")
        check2 = limiter.check("user:1")

        assert check1.remaining == check2.remaining
        assert check1.allowed is True

    def test_reset_clears_count(self):
        """reset() should restore full capacity for a key."""
        limiter = FixedWindowLimiter(limit=2, window_seconds=60)

        limiter.consume("user:1")
        limiter.consume("user:1")
        denied = limiter.consume("user:1")
        assert denied.allowed is False

        limiter.reset("user:1")

        result = limiter.consume("user:1")
        assert result.allowed is True
        assert result.remaining == 1


# ---------------------------------------------------------------------------
# SlidingWindowLimiter
# ---------------------------------------------------------------------------

class TestSlidingWindowLimiter:
    """Tests for the SlidingWindowLimiter."""

    def test_consume_within_limit(self):
        """Requests within the limit should be allowed."""
        limiter = SlidingWindowLimiter(limit=5, window_seconds=60)

        for i in range(5):
            result = limiter.consume("client:a")
            assert result.allowed is True
            assert result.remaining == 5 - (i + 1)

    def test_enforce_limit(self):
        """Exceeding the limit should deny the request."""
        limiter = SlidingWindowLimiter(limit=3, window_seconds=60)

        for _ in range(3):
            limiter.consume("client:a")

        denied = limiter.consume("client:a")
        assert denied.allowed is False
        assert denied.remaining == 0
        assert denied.retry_after is not None

    def test_separate_keys_are_independent(self):
        """Different keys should have independent sliding windows."""
        limiter = SlidingWindowLimiter(limit=2, window_seconds=60)

        limiter.consume("client:a")
        limiter.consume("client:a")
        denied = limiter.consume("client:a")
        assert denied.allowed is False

        result = limiter.consume("client:b")
        assert result.allowed is True
        assert result.remaining == 1


# ---------------------------------------------------------------------------
# TokenBucketLimiter
# ---------------------------------------------------------------------------

class TestTokenBucketLimiter:
    """Tests for the TokenBucketLimiter."""

    def test_consume_tokens(self):
        """Consuming tokens should reduce the remaining count."""
        limiter = TokenBucketLimiter(capacity=10, refill_rate=1.0)

        result = limiter.consume("key:1", tokens=3)
        assert result.allowed is True
        assert result.remaining == 7

    def test_burst_capacity(self):
        """All tokens in the bucket can be consumed at once (burst)."""
        limiter = TokenBucketLimiter(capacity=5, refill_rate=1.0)

        result = limiter.consume("key:1", tokens=5)
        assert result.allowed is True
        assert result.remaining == 0

        denied = limiter.consume("key:1", tokens=1)
        assert denied.allowed is False
        assert denied.retry_after is not None
        assert denied.retry_after > 0

    def test_refill_after_sleep(self):
        """Tokens should refill over time based on refill_rate."""
        limiter = TokenBucketLimiter(capacity=10, refill_rate=100.0, initial_tokens=0)

        denied = limiter.consume("key:1")
        assert denied.allowed is False

        time.sleep(0.05)

        result = limiter.consume("key:1")
        assert result.allowed is True

    def test_initial_tokens(self):
        """initial_tokens should control the starting token count."""
        limiter = TokenBucketLimiter(capacity=10, refill_rate=1.0, initial_tokens=2)

        result = limiter.consume("key:1", tokens=2)
        assert result.allowed is True
        assert result.remaining == 0

        denied = limiter.consume("key:1", tokens=1)
        assert denied.allowed is False


# ---------------------------------------------------------------------------
# CompositeRateLimiter
# ---------------------------------------------------------------------------

class TestCompositeRateLimiter:
    """Tests for the CompositeRateLimiter."""

    def test_most_restrictive_wins(self):
        """The most restrictive limiter should determine the result."""
        strict = FixedWindowLimiter(limit=2, window_seconds=60)
        lenient = FixedWindowLimiter(limit=100, window_seconds=60)

        composite = CompositeRateLimiter({"strict": strict, "lenient": lenient})

        composite.consume("key:1")
        composite.consume("key:1")

        denied = composite.consume("key:1")
        assert denied.allowed is False

    def test_check_returns_least_remaining(self):
        """check() should return the result with the fewest remaining tokens."""
        strict = FixedWindowLimiter(limit=3, window_seconds=60)
        lenient = FixedWindowLimiter(limit=100, window_seconds=60)

        composite = CompositeRateLimiter({"strict": strict, "lenient": lenient})

        composite.consume("key:1")
        composite.consume("key:1")

        result = composite.check("key:1")
        assert result.allowed is True
        assert result.remaining == 1

    def test_reset_all(self):
        """reset() should clear state in all child limiters."""
        limiter_a = FixedWindowLimiter(limit=1, window_seconds=60)
        limiter_b = FixedWindowLimiter(limit=1, window_seconds=60)

        composite = CompositeRateLimiter({"a": limiter_a, "b": limiter_b})

        composite.consume("key:1")
        denied = composite.consume("key:1")
        assert denied.allowed is False

        composite.reset("key:1")

        result = composite.consume("key:1")
        assert result.allowed is True


# ---------------------------------------------------------------------------
# RateLimiterMiddleware
# ---------------------------------------------------------------------------

class TestRateLimiterMiddleware:
    """Tests for the RateLimiterMiddleware wrapper."""

    def test_check_calls_consume(self):
        """Middleware check() should consume a token (delegates to limiter.consume)."""
        limiter = FixedWindowLimiter(limit=2, window_seconds=60)
        middleware = RateLimiterMiddleware(limiter)

        result1 = middleware.check("ip:1")
        assert result1.allowed is True

        result2 = middleware.check("ip:1")
        assert result2.allowed is True

        result3 = middleware.check("ip:1")
        assert result3.allowed is False

    def test_would_allow_does_not_consume(self):
        """would_allow() should inspect without consuming tokens."""
        limiter = FixedWindowLimiter(limit=2, window_seconds=60)
        middleware = RateLimiterMiddleware(limiter)

        assert middleware.would_allow("ip:1") is True
        assert middleware.would_allow("ip:1") is True
        assert middleware.would_allow("ip:1") is True

        result = middleware.check("ip:1")
        assert result.allowed is True
        assert result.remaining == 1


# ---------------------------------------------------------------------------
# create_rate_limiter factory
# ---------------------------------------------------------------------------

class TestCreateRateLimiter:
    """Tests for the create_rate_limiter factory function."""

    def test_creates_fixed_window(self):
        """Factory should produce a FixedWindowLimiter."""
        limiter = create_rate_limiter("fixed_window", limit=10, window_seconds=30)
        assert isinstance(limiter, FixedWindowLimiter)

    def test_creates_sliding_window(self):
        """Factory should produce a SlidingWindowLimiter."""
        limiter = create_rate_limiter("sliding_window", limit=20, window_seconds=60)
        assert isinstance(limiter, SlidingWindowLimiter)

    def test_creates_token_bucket(self):
        """Factory should produce a TokenBucketLimiter."""
        limiter = create_rate_limiter("token_bucket", capacity=50, refill_rate=5.0)
        assert isinstance(limiter, TokenBucketLimiter)

    def test_unknown_type_raises_value_error(self):
        """An unrecognized limiter type should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown limiter type"):
            create_rate_limiter("leaky_bucket", capacity=10)
