"""Tests for cloud.common.rate_limiter — TokenBucketLimiter.

Zero-Mock: All tests use real token-bucket logic with real time.
"""

from __future__ import annotations

import threading
import time

import pytest

from codomyrmex.cloud.common.rate_limiter import (
    RateLimiterConfig,
    TokenBucketLimiter,
    get_provider_limiter,
    rate_limited,
    reset_all_limiters,
)

# ── Config defaults ──────────────────────────────────────────────────


class TestRateLimiterConfig:
    """Verify RateLimiterConfig default values."""

    def test_defaults(self) -> None:
        cfg = RateLimiterConfig()
        assert cfg.max_requests_per_second == 10.0
        assert cfg.burst_size == 20
        assert cfg.retry_after_seconds == 1.0
        assert cfg.provider_name == "unknown"

    def test_custom_values(self) -> None:
        cfg = RateLimiterConfig(
            max_requests_per_second=5.0,
            burst_size=10,
            retry_after_seconds=2.0,
            provider_name="aws",
        )
        assert cfg.max_requests_per_second == 5.0
        assert cfg.burst_size == 10
        assert cfg.provider_name == "aws"


# ── Token acquisition ────────────────────────────────────────────────


class TestTokenBucketLimiter:
    """Test real token-bucket behaviour."""

    def test_initial_tokens_equal_burst(self) -> None:
        limiter = TokenBucketLimiter(RateLimiterConfig(burst_size=5))
        assert limiter.remaining_tokens == pytest.approx(5.0, abs=0.5)

    def test_try_acquire_succeeds(self) -> None:
        limiter = TokenBucketLimiter(
            RateLimiterConfig(max_requests_per_second=100, burst_size=10)
        )
        assert limiter.try_acquire() is True
        assert limiter.total_acquired == 1

    def test_try_acquire_drains_tokens(self) -> None:
        limiter = TokenBucketLimiter(
            RateLimiterConfig(max_requests_per_second=1, burst_size=2)
        )
        assert limiter.try_acquire() is True
        assert limiter.try_acquire() is True
        # Third should fail (burst exhausted, not enough time to refill)
        assert limiter.try_acquire() is False

    def test_wait_blocks_until_available(self) -> None:
        limiter = TokenBucketLimiter(
            RateLimiterConfig(max_requests_per_second=100, burst_size=1)
        )
        # Drain the single token
        assert limiter.try_acquire() is True
        # wait should block briefly then succeed
        t0 = time.monotonic()
        assert limiter.wait(timeout=1.0) is True
        elapsed = time.monotonic() - t0
        assert elapsed < 1.0

    def test_wait_timeout_expires(self) -> None:
        limiter = TokenBucketLimiter(
            RateLimiterConfig(max_requests_per_second=0.5, burst_size=1)
        )
        assert limiter.try_acquire() is True
        # Very short timeout — should fail
        assert limiter.wait(timeout=0.05) is False

    def test_wait_raises_on_excess_tokens(self) -> None:
        limiter = TokenBucketLimiter(RateLimiterConfig(burst_size=3))
        with pytest.raises(ValueError, match="burst_size"):
            limiter.wait(tokens=5)

    def test_refill_over_time(self) -> None:
        limiter = TokenBucketLimiter(
            RateLimiterConfig(max_requests_per_second=100, burst_size=5)
        )
        # Drain everything
        for _ in range(5):
            limiter.try_acquire()
        # Wait a little for refill
        time.sleep(0.05)
        assert limiter.remaining_tokens > 0

    def test_handle_retry_after(self) -> None:
        limiter = TokenBucketLimiter(
            RateLimiterConfig(max_requests_per_second=100, burst_size=10)
        )
        # After handle_retry_after tokens should be 0
        limiter.handle_retry_after(retry_after=0.01)
        assert limiter.remaining_tokens == pytest.approx(0.0, abs=1.5)

    def test_thread_safety(self) -> None:
        limiter = TokenBucketLimiter(
            RateLimiterConfig(max_requests_per_second=1000, burst_size=100)
        )
        results: list[bool] = []
        lock = threading.Lock()

        def acquire_many() -> None:
            for _ in range(20):
                r = limiter.try_acquire()
                with lock:
                    results.append(r)

        threads = [threading.Thread(target=acquire_many) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All 100 acquires should have succeeded (burst=100)
        assert len(results) == 100
        assert all(results)

    def test_total_waited_seconds_tracked(self) -> None:
        limiter = TokenBucketLimiter(
            RateLimiterConfig(max_requests_per_second=100, burst_size=1)
        )
        limiter.try_acquire()  # drain
        limiter.wait(timeout=1.0)
        assert limiter.total_waited_seconds >= 0


# ── Decorator ─────────────────────────────────────────────────────────


class TestRateLimitedDecorator:
    """Test the @rate_limited decorator."""

    def test_decorator_acquires_token(self) -> None:
        limiter = TokenBucketLimiter(
            RateLimiterConfig(max_requests_per_second=100, burst_size=10)
        )

        @rate_limited(limiter)
        def my_func() -> str:
            return "ok"

        result = my_func()
        assert result == "ok"
        assert limiter.total_acquired >= 1


# ── Registry ──────────────────────────────────────────────────────────


class TestProviderLimiterRegistry:
    """Test get_provider_limiter and reset_all_limiters."""

    def setup_method(self) -> None:
        reset_all_limiters()

    def teardown_method(self) -> None:
        reset_all_limiters()

    def test_get_creates_and_returns_same_instance(self) -> None:
        limiter1 = get_provider_limiter("test_provider")
        limiter2 = get_provider_limiter("test_provider")
        assert limiter1 is limiter2

    def test_different_providers_get_different_limiters(self) -> None:
        a = get_provider_limiter("aws")
        b = get_provider_limiter("gcp")
        assert a is not b

    def test_custom_config_applied(self) -> None:
        cfg = RateLimiterConfig(max_requests_per_second=42, provider_name="custom")
        limiter = get_provider_limiter("custom", config=cfg)
        assert limiter.config.max_requests_per_second == 42

    def test_reset_clears_all(self) -> None:
        get_provider_limiter("a")
        get_provider_limiter("b")
        reset_all_limiters()
        # After reset, a new instance should be created
        limiter = get_provider_limiter("a")
        assert limiter.total_acquired == 0
