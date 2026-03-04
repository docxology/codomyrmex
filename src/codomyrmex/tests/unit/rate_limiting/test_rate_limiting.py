"""Tests for rate_limiting module."""


import pytest

try:
    from codomyrmex.api.rate_limiting import (
        FixedWindowLimiter,
        QuotaManager,
        RateLimitExceeded,
        RateLimitResult,
        SlidingWindowLimiter,
        TokenBucketLimiter,
        create_limiter,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("rate_limiting module not available", allow_module_level=True)


@pytest.mark.unit
class TestRateLimitResult:
    """Test suite for RateLimitResult."""
    def test_create_result(self):
        """Verify create result behavior."""
        result = RateLimitResult(allowed=True, remaining=5, limit=10)
        assert result.allowed is True
        assert result.remaining == 5
        assert result.limit == 10

    def test_denied_result(self):
        """Verify denied result behavior."""
        result = RateLimitResult(allowed=False, remaining=0, limit=10)
        assert result.allowed is False
        assert result.remaining == 0

    def test_headers(self):
        """Verify headers behavior."""
        result = RateLimitResult(allowed=True, remaining=5, limit=10)
        headers = result.headers
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers


@pytest.mark.unit
class TestFixedWindowLimiter:
    """Test suite for FixedWindowLimiter."""
    def test_create_limiter(self):
        """Verify create limiter behavior."""
        limiter = FixedWindowLimiter(limit=10, window_seconds=60)
        assert limiter is not None

    def test_allows_within_limit(self):
        """Verify allows within limit behavior."""
        limiter = FixedWindowLimiter(limit=5, window_seconds=60)
        for _ in range(5):
            result = limiter.acquire("test_key")
            assert result.allowed is True

    def test_denies_over_limit(self):
        """Verify denies over limit behavior."""
        limiter = FixedWindowLimiter(limit=2, window_seconds=60)
        limiter.acquire("test_key")
        limiter.acquire("test_key")
        with pytest.raises(RateLimitExceeded):
            limiter.acquire("test_key")

    def test_separate_keys(self):
        """Verify separate keys behavior."""
        limiter = FixedWindowLimiter(limit=1, window_seconds=60)
        result1 = limiter.acquire("key_a")
        result2 = limiter.acquire("key_b")
        assert result1.allowed is True
        assert result2.allowed is True

    def test_remaining_count(self):
        """Verify remaining count behavior."""
        limiter = FixedWindowLimiter(limit=3, window_seconds=60)
        result = limiter.acquire("test_key")
        assert result.remaining == 2


@pytest.mark.unit
class TestSlidingWindowLimiter:
    """Test suite for SlidingWindowLimiter."""
    def test_create_limiter(self):
        """Verify create limiter behavior."""
        limiter = SlidingWindowLimiter(limit=10, window_seconds=60)
        assert limiter is not None

    def test_allows_within_limit(self):
        """Verify allows within limit behavior."""
        limiter = SlidingWindowLimiter(limit=3, window_seconds=60)
        for _ in range(3):
            result = limiter.acquire("test_key")
            assert result.allowed is True

    def test_denies_over_limit(self):
        """Verify denies over limit behavior."""
        limiter = SlidingWindowLimiter(limit=1, window_seconds=60)
        limiter.acquire("test_key")
        with pytest.raises(RateLimitExceeded):
            limiter.acquire("test_key")


@pytest.mark.unit
class TestTokenBucketLimiter:
    """Test suite for TokenBucketLimiter."""
    def test_create_limiter(self):
        """Verify create limiter behavior."""
        limiter = TokenBucketLimiter(capacity=10, refill_rate=1.0)
        assert limiter is not None

    def test_allows_within_capacity(self):
        """Verify allows within capacity behavior."""
        limiter = TokenBucketLimiter(capacity=5, refill_rate=1.0)
        for _ in range(5):
            result = limiter.acquire("test_key")
            assert result.allowed is True

    def test_denies_when_empty(self):
        """Verify denies when empty behavior."""
        limiter = TokenBucketLimiter(capacity=1, refill_rate=0.01)
        limiter.acquire("test_key")
        with pytest.raises(RateLimitExceeded):
            limiter.acquire("test_key")


@pytest.mark.unit
class TestRateLimitExceeded:
    """Test suite for RateLimitExceeded."""
    def test_exception_is_raised(self):
        """Verify exception is raised behavior."""
        with pytest.raises(RateLimitExceeded):
            raise RateLimitExceeded("Rate limit exceeded")

    def test_exception_message(self):
        """Verify exception message behavior."""
        exc = RateLimitExceeded("Too many requests")
        assert "Too many requests" in str(exc)


@pytest.mark.unit
class TestQuotaManager:
    """Test suite for QuotaManager."""
    def test_create_manager(self):
        """Verify create manager behavior."""
        manager = QuotaManager()
        assert manager is not None


@pytest.mark.unit
class TestCreateLimiter:
    """Test suite for CreateLimiter."""
    def test_factory_creates_limiter(self):
        """Verify factory creates limiter behavior."""
        limiter = create_limiter(algorithm="fixed_window", limit=10, window_seconds=60)
        assert limiter is not None

    def test_factory_returns_correct_type(self):
        """Verify factory returns correct type behavior."""
        limiter = create_limiter(algorithm="token_bucket", limit=10)
        assert isinstance(limiter, TokenBucketLimiter)
