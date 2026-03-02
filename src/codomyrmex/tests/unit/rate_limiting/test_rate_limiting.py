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
        """Test functionality: create result."""
        result = RateLimitResult(allowed=True, remaining=5, limit=10)
        assert result.allowed is True
        assert result.remaining == 5
        assert result.limit == 10

    def test_denied_result(self):
        """Test functionality: denied result."""
        result = RateLimitResult(allowed=False, remaining=0, limit=10)
        assert result.allowed is False
        assert result.remaining == 0

    def test_headers(self):
        """Test functionality: headers."""
        result = RateLimitResult(allowed=True, remaining=5, limit=10)
        headers = result.headers
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers


@pytest.mark.unit
class TestFixedWindowLimiter:
    """Test suite for FixedWindowLimiter."""
    def test_create_limiter(self):
        """Test functionality: create limiter."""
        limiter = FixedWindowLimiter(limit=10, window_seconds=60)
        assert limiter is not None

    def test_allows_within_limit(self):
        """Test functionality: allows within limit."""
        limiter = FixedWindowLimiter(limit=5, window_seconds=60)
        for _ in range(5):
            result = limiter.acquire("test_key")
            assert result.allowed is True

    def test_denies_over_limit(self):
        """Test functionality: denies over limit."""
        limiter = FixedWindowLimiter(limit=2, window_seconds=60)
        limiter.acquire("test_key")
        limiter.acquire("test_key")
        with pytest.raises(RateLimitExceeded):
            limiter.acquire("test_key")

    def test_separate_keys(self):
        """Test functionality: separate keys."""
        limiter = FixedWindowLimiter(limit=1, window_seconds=60)
        result1 = limiter.acquire("key_a")
        result2 = limiter.acquire("key_b")
        assert result1.allowed is True
        assert result2.allowed is True

    def test_remaining_count(self):
        """Test functionality: remaining count."""
        limiter = FixedWindowLimiter(limit=3, window_seconds=60)
        result = limiter.acquire("test_key")
        assert result.remaining == 2


@pytest.mark.unit
class TestSlidingWindowLimiter:
    """Test suite for SlidingWindowLimiter."""
    def test_create_limiter(self):
        """Test functionality: create limiter."""
        limiter = SlidingWindowLimiter(limit=10, window_seconds=60)
        assert limiter is not None

    def test_allows_within_limit(self):
        """Test functionality: allows within limit."""
        limiter = SlidingWindowLimiter(limit=3, window_seconds=60)
        for _ in range(3):
            result = limiter.acquire("test_key")
            assert result.allowed is True

    def test_denies_over_limit(self):
        """Test functionality: denies over limit."""
        limiter = SlidingWindowLimiter(limit=1, window_seconds=60)
        limiter.acquire("test_key")
        with pytest.raises(RateLimitExceeded):
            limiter.acquire("test_key")


@pytest.mark.unit
class TestTokenBucketLimiter:
    """Test suite for TokenBucketLimiter."""
    def test_create_limiter(self):
        """Test functionality: create limiter."""
        limiter = TokenBucketLimiter(capacity=10, refill_rate=1.0)
        assert limiter is not None

    def test_allows_within_capacity(self):
        """Test functionality: allows within capacity."""
        limiter = TokenBucketLimiter(capacity=5, refill_rate=1.0)
        for _ in range(5):
            result = limiter.acquire("test_key")
            assert result.allowed is True

    def test_denies_when_empty(self):
        """Test functionality: denies when empty."""
        limiter = TokenBucketLimiter(capacity=1, refill_rate=0.01)
        limiter.acquire("test_key")
        with pytest.raises(RateLimitExceeded):
            limiter.acquire("test_key")


@pytest.mark.unit
class TestRateLimitExceeded:
    """Test suite for RateLimitExceeded."""
    def test_exception_is_raised(self):
        """Test functionality: exception is raised."""
        with pytest.raises(RateLimitExceeded):
            raise RateLimitExceeded("Rate limit exceeded")

    def test_exception_message(self):
        """Test functionality: exception message."""
        exc = RateLimitExceeded("Too many requests")
        assert "Too many requests" in str(exc)


@pytest.mark.unit
class TestQuotaManager:
    """Test suite for QuotaManager."""
    def test_create_manager(self):
        """Test functionality: create manager."""
        manager = QuotaManager()
        assert manager is not None


@pytest.mark.unit
class TestCreateLimiter:
    """Test suite for CreateLimiter."""
    def test_factory_creates_limiter(self):
        """Test functionality: factory creates limiter."""
        limiter = create_limiter(algorithm="fixed_window", limit=10, window_seconds=60)
        assert limiter is not None

    def test_factory_returns_correct_type(self):
        """Test functionality: factory returns correct type."""
        limiter = create_limiter(algorithm="token_bucket", limit=10)
        assert isinstance(limiter, TokenBucketLimiter)
