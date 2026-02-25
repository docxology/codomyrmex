"""Tests for rate_limiting.distributed module."""

import time

import pytest

try:
    from codomyrmex.api.rate_limiting import (
        RateLimitExceeded,
        RateLimitResult,
    )
    from codomyrmex.api.rate_limiting.distributed import (
        AdaptiveRateLimiter,
        LeakyBucketLimiter,
        RedisRateLimiter,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("rate_limiting.distributed module not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# RedisRateLimiter (local fallback mode, no Redis needed)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRedisRateLimiterLocalFallback:
    """Test RedisRateLimiter using its in-memory fallback (no Redis)."""

    def test_create_without_redis(self):
        """Test functionality: create without redis."""
        limiter = RedisRateLimiter(limit=10, window_seconds=60)
        assert limiter.limit == 10
        assert limiter.window_seconds == 60

    def test_check_within_limit(self):
        """Test functionality: check within limit."""
        limiter = RedisRateLimiter(limit=5, window_seconds=60)
        result = limiter.check("user1")
        assert isinstance(result, RateLimitResult)
        assert result.allowed is True
        assert result.remaining == 5

    def test_acquire_within_limit(self):
        """Test functionality: acquire within limit."""
        limiter = RedisRateLimiter(limit=5, window_seconds=60)
        result = limiter.acquire("user1")
        assert result.allowed is True
        assert result.remaining == 4
        assert result.limit == 5

    def test_acquire_multiple(self):
        """Test functionality: acquire multiple."""
        limiter = RedisRateLimiter(limit=3, window_seconds=60)
        limiter.acquire("user1")
        limiter.acquire("user1")
        result = limiter.acquire("user1")
        assert result.allowed is True
        assert result.remaining == 0

    def test_acquire_exceeds_limit(self):
        """Test functionality: acquire exceeds limit."""
        limiter = RedisRateLimiter(limit=2, window_seconds=60)
        limiter.acquire("user1")
        limiter.acquire("user1")
        with pytest.raises(RateLimitExceeded):
            limiter.acquire("user1")

    def test_reset_clears_count(self):
        """Test functionality: reset clears count."""
        limiter = RedisRateLimiter(limit=2, window_seconds=60)
        limiter.acquire("user1")
        limiter.acquire("user1")
        limiter.reset("user1")
        result = limiter.check("user1")
        assert result.allowed is True
        assert result.remaining == 2

    def test_different_keys_independent(self):
        """Test functionality: different keys independent."""
        limiter = RedisRateLimiter(limit=1, window_seconds=60)
        limiter.acquire("user1")
        result = limiter.check("user2")
        assert result.allowed is True

    def test_custom_key_prefix(self):
        """Test functionality: custom key prefix."""
        limiter = RedisRateLimiter(limit=5, window_seconds=60, key_prefix="custom:")
        assert limiter.key_prefix == "custom:"

    def test_acquire_with_cost(self):
        """Test functionality: acquire with cost."""
        limiter = RedisRateLimiter(limit=5, window_seconds=60)
        result = limiter.acquire("user1", cost=3)
        assert result.allowed is True
        assert result.remaining == 2

    def test_check_with_cost(self):
        """Test functionality: check with cost."""
        limiter = RedisRateLimiter(limit=5, window_seconds=60)
        limiter.acquire("user1", cost=4)
        result = limiter.check("user1", cost=2)
        assert result.allowed is False


# ---------------------------------------------------------------------------
# LeakyBucketLimiter
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestLeakyBucketLimiter:
    """Test suite for LeakyBucketLimiter."""
    def test_create(self):
        """Test functionality: create."""
        limiter = LeakyBucketLimiter(capacity=10, leak_rate=1.0)
        assert limiter.capacity == 10
        assert limiter.leak_rate == 1.0

    def test_check_empty_bucket(self):
        """Test functionality: check empty bucket."""
        limiter = LeakyBucketLimiter(capacity=5, leak_rate=1.0)
        result = limiter.check("user1")
        assert result.allowed is True
        assert result.remaining == 5
        assert result.limit == 5

    def test_acquire_fills_bucket(self):
        """Test functionality: acquire fills bucket."""
        limiter = LeakyBucketLimiter(capacity=5, leak_rate=1.0)
        result = limiter.acquire("user1")
        assert result.allowed is True
        assert result.remaining == 4

    def test_acquire_until_full(self):
        """Test functionality: acquire until full."""
        limiter = LeakyBucketLimiter(capacity=3, leak_rate=0.001)
        limiter.acquire("user1")
        limiter.acquire("user1")
        limiter.acquire("user1")
        with pytest.raises(RateLimitExceeded):
            limiter.acquire("user1")

    def test_bucket_leaks_over_time(self):
        """Test functionality: bucket leaks over time."""
        limiter = LeakyBucketLimiter(capacity=2, leak_rate=100.0)
        limiter.acquire("user1")
        limiter.acquire("user1")
        # Wait for leak
        time.sleep(0.05)
        result = limiter.check("user1")
        assert result.allowed is True

    def test_reset_empties_bucket(self):
        """Test functionality: reset empties bucket."""
        limiter = LeakyBucketLimiter(capacity=2, leak_rate=0.001)
        limiter.acquire("user1")
        limiter.acquire("user1")
        limiter.reset("user1")
        result = limiter.check("user1")
        assert result.allowed is True
        assert result.remaining == 2

    def test_rate_limit_exceeded_has_retry_after(self):
        """Test functionality: rate limit exceeded has retry after."""
        limiter = LeakyBucketLimiter(capacity=1, leak_rate=1.0)
        limiter.acquire("user1")
        with pytest.raises(RateLimitExceeded) as exc_info:
            limiter.acquire("user1")
        assert exc_info.value.retry_after is not None
        assert exc_info.value.retry_after > 0

    def test_acquire_with_cost(self):
        """Test functionality: acquire with cost."""
        limiter = LeakyBucketLimiter(capacity=5, leak_rate=1.0)
        result = limiter.acquire("user1", cost=3)
        assert result.allowed is True
        assert result.remaining == 2

    def test_different_keys_independent(self):
        """Test functionality: different keys independent."""
        limiter = LeakyBucketLimiter(capacity=1, leak_rate=0.001)
        limiter.acquire("user1")
        result = limiter.acquire("user2")
        assert result.allowed is True


# ---------------------------------------------------------------------------
# AdaptiveRateLimiter
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAdaptiveRateLimiter:
    """Test suite for AdaptiveRateLimiter."""
    def test_create(self):
        """Test functionality: create."""
        limiter = AdaptiveRateLimiter(base_limit=100, window_seconds=60)
        assert limiter.base_limit == 100
        assert limiter.window_seconds == 60

    def test_normal_load_uses_base_limit(self):
        """Test functionality: normal load uses base limit."""
        limiter = AdaptiveRateLimiter(base_limit=10, window_seconds=60)
        limiter.set_load(0.5)
        result = limiter.check("user1")
        assert result.limit == 10

    def test_high_load_reduces_limit(self):
        """Test functionality: high load reduces limit."""
        limiter = AdaptiveRateLimiter(
            base_limit=100,
            window_seconds=60,
            load_threshold=0.8,
        )
        limiter.set_load(0.9)
        result = limiter.check("user1")
        assert result.limit < 100

    def test_max_load_uses_min_ratio(self):
        """Test functionality: max load uses min ratio."""
        limiter = AdaptiveRateLimiter(
            base_limit=100,
            window_seconds=60,
            load_threshold=0.5,
            min_limit_ratio=0.2,
        )
        limiter.set_load(1.0)
        result = limiter.check("user1")
        assert result.limit == 20  # 100 * 0.2

    def test_set_load_clamps_to_range(self):
        """Test functionality: set load clamps to range."""
        limiter = AdaptiveRateLimiter(base_limit=100, window_seconds=60)
        limiter.set_load(-0.5)
        assert limiter._current_load == 0.0
        limiter.set_load(1.5)
        assert limiter._current_load == 1.0

    def test_acquire_within_limit(self):
        """Test functionality: acquire within limit."""
        limiter = AdaptiveRateLimiter(base_limit=5, window_seconds=60)
        for _ in range(5):
            result = limiter.acquire("user1")
            assert result.allowed is True

    def test_acquire_exceeds_limit(self):
        """Test functionality: acquire exceeds limit."""
        limiter = AdaptiveRateLimiter(base_limit=2, window_seconds=60)
        limiter.acquire("user1")
        limiter.acquire("user1")
        with pytest.raises(RateLimitExceeded):
            limiter.acquire("user1")

    def test_reset_clears_requests(self):
        """Test functionality: reset clears requests."""
        limiter = AdaptiveRateLimiter(base_limit=2, window_seconds=60)
        limiter.acquire("user1")
        limiter.acquire("user1")
        limiter.reset("user1")
        result = limiter.check("user1")
        assert result.allowed is True

    def test_acquire_with_cost(self):
        """Test functionality: acquire with cost."""
        limiter = AdaptiveRateLimiter(base_limit=5, window_seconds=60)
        result = limiter.acquire("user1", cost=3)
        assert result.allowed is True
        assert result.remaining == 2

    def test_check_reflects_current_count(self):
        """Test functionality: check reflects current count."""
        limiter = AdaptiveRateLimiter(base_limit=5, window_seconds=60)
        limiter.acquire("user1", cost=3)
        result = limiter.check("user1")
        assert result.remaining == 2

    def test_load_below_threshold_full_limit(self):
        """Test functionality: load below threshold full limit."""
        limiter = AdaptiveRateLimiter(
            base_limit=100,
            window_seconds=60,
            load_threshold=0.8,
        )
        limiter.set_load(0.0)
        result = limiter.check("user1")
        assert result.limit == 100

    def test_different_keys_independent(self):
        """Test functionality: different keys independent."""
        limiter = AdaptiveRateLimiter(base_limit=1, window_seconds=60)
        limiter.acquire("user1")
        result = limiter.acquire("user2")
        assert result.allowed is True
