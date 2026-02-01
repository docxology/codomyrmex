"""
Tests for API Rate Limiter Module
"""

import pytest
import time
from codomyrmex.api.rate_limiter import (
    RateLimitResult,
    FixedWindowLimiter,
    TokenBucketLimiter,
    SlidingWindowLimiter,
    RateLimiterMiddleware,
)


class TestRateLimitResult:
    """Tests for RateLimitResult."""
    
    def test_to_headers(self):
        """Should convert to headers."""
        result = RateLimitResult(allowed=True, remaining=99)
        headers = result.to_headers()
        
        assert "X-RateLimit-Remaining" in headers
        assert headers["X-RateLimit-Remaining"] == "99"


class TestFixedWindowLimiter:
    """Tests for FixedWindowLimiter."""
    
    def test_acquire(self):
        """Should acquire within limit."""
        limiter = FixedWindowLimiter(limit=10, window_seconds=60)
        
        result = limiter.acquire("user:1")
        
        assert result.allowed
        assert result.remaining == 9
    
    def test_rate_limit(self):
        """Should rate limit after threshold."""
        limiter = FixedWindowLimiter(limit=3, window_seconds=60)
        
        limiter.acquire("user:1")
        limiter.acquire("user:1")
        limiter.acquire("user:1")
        result = limiter.acquire("user:1")
        
        assert not result.allowed
        assert result.retry_after_seconds > 0
    
    def test_separate_keys(self):
        """Should track keys separately."""
        limiter = FixedWindowLimiter(limit=2, window_seconds=60)
        
        limiter.acquire("user:1")
        limiter.acquire("user:1")
        result = limiter.acquire("user:2")
        
        assert result.allowed


class TestTokenBucketLimiter:
    """Tests for TokenBucketLimiter."""
    
    def test_acquire(self):
        """Should acquire tokens."""
        limiter = TokenBucketLimiter(capacity=10, refill_rate=10)
        
        result = limiter.acquire("api:key")
        
        assert result.allowed
        assert result.remaining == 9
    
    def test_burst(self):
        """Should allow bursting."""
        limiter = TokenBucketLimiter(capacity=5, refill_rate=1)
        
        # Use all tokens quickly
        for _ in range(5):
            result = limiter.acquire("key")
            assert result.allowed
        
        # Next should fail
        result = limiter.acquire("key")
        assert not result.allowed
    
    def test_refill(self):
        """Should refill tokens."""
        limiter = TokenBucketLimiter(capacity=10, refill_rate=100)  # 100/sec
        
        limiter.acquire("key", cost=10)  # Use all
        time.sleep(0.05)  # Wait for refill
        
        result = limiter.acquire("key", cost=3)
        assert result.allowed


class TestSlidingWindowLimiter:
    """Tests for SlidingWindowLimiter."""
    
    def test_acquire(self):
        """Should acquire within limit."""
        limiter = SlidingWindowLimiter(limit=10, window_seconds=60)
        
        result = limiter.acquire("user:1")
        
        assert result.allowed
    
    def test_sliding_limit(self):
        """Should enforce limit."""
        limiter = SlidingWindowLimiter(limit=3, window_seconds=60)
        
        for _ in range(3):
            limiter.acquire("key")
        
        result = limiter.acquire("key")
        
        assert not result.allowed


class TestRateLimiterMiddleware:
    """Tests for RateLimiterMiddleware."""
    
    def test_check(self):
        """Should check rate limit."""
        limiter = FixedWindowLimiter(limit=10, window_seconds=60)
        middleware = RateLimiterMiddleware(limiter)
        
        result = middleware.check("client:1")
        
        assert result.allowed
    
    def test_would_allow(self):
        """Should check without consuming."""
        limiter = FixedWindowLimiter(limit=10, window_seconds=60)
        middleware = RateLimiterMiddleware(limiter)
        
        # Check without consuming
        assert middleware.would_allow("client:1")
        
        # Value should still be at limit
        result = middleware.check("client:1")
        assert result.remaining == 9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
