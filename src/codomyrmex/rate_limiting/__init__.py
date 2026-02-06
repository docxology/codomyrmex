"""
Rate Limiting Module

API rate limiting, throttling, and quota management.
"""

__version__ = "0.1.0"

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from collections import deque


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool
    remaining: int
    limit: int
    reset_at: Optional[datetime] = None
    retry_after: Optional[float] = None
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get rate limit headers for HTTP responses."""
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(self.remaining),
        }
        if self.reset_at:
            headers["X-RateLimit-Reset"] = str(int(self.reset_at.timestamp()))
        if self.retry_after:
            headers["Retry-After"] = str(int(self.retry_after))
        return headers


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""
    
    @abstractmethod
    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """
        Check if request is allowed without consuming quota.
        
        Args:
            key: Identifier (e.g., user ID, IP address)
            cost: Request cost (default 1)
            
        Returns:
            RateLimitResult indicating if allowed
        """
        pass
    
    @abstractmethod
    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """
        Acquire quota for a request.
        
        Args:
            key: Identifier
            cost: Request cost
            
        Returns:
            RateLimitResult (raises RateLimitExceeded if over limit)
        """
        pass
    
    @abstractmethod
    def reset(self, key: str) -> None:
        """Reset quota for a key."""
        pass


class FixedWindowLimiter(RateLimiter):
    """Fixed window rate limiter."""
    
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._counts: Dict[str, Tuple[int, datetime]] = {}
        self._lock = threading.Lock()
    
    def _get_window_start(self) -> datetime:
        """Get current window start time."""
        now = datetime.now()
        seconds = now.timestamp()
        window_start = seconds - (seconds % self.window_seconds)
        return datetime.fromtimestamp(window_start)
    
    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check without consuming."""
        window_start = self._get_window_start()
        reset_at = window_start + timedelta(seconds=self.window_seconds)
        
        with self._lock:
            if key in self._counts:
                count, window = self._counts[key]
                if window == window_start:
                    remaining = max(0, self.limit - count)
                    return RateLimitResult(
                        allowed=remaining >= cost,
                        remaining=remaining,
                        limit=self.limit,
                        reset_at=reset_at,
                    )
            
            return RateLimitResult(
                allowed=True,
                remaining=self.limit,
                limit=self.limit,
                reset_at=reset_at,
            )
    
    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire quota."""
        window_start = self._get_window_start()
        reset_at = window_start + timedelta(seconds=self.window_seconds)
        
        with self._lock:
            if key in self._counts:
                count, window = self._counts[key]
                if window != window_start:
                    # New window, reset count
                    count = 0
            else:
                count = 0
            
            if count + cost > self.limit:
                retry_after = (reset_at - datetime.now()).total_seconds()
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {key}",
                    retry_after=retry_after,
                )
            
            self._counts[key] = (count + cost, window_start)
            remaining = self.limit - count - cost
            
            return RateLimitResult(
                allowed=True,
                remaining=remaining,
                limit=self.limit,
                reset_at=reset_at,
            )
    
    def reset(self, key: str) -> None:
        """Reset quota for key."""
        with self._lock:
            if key in self._counts:
                del self._counts[key]


class SlidingWindowLimiter(RateLimiter):
    """Sliding window rate limiter."""
    
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: Dict[str, deque] = {}
        self._lock = threading.Lock()
    
    def _clean_old_requests(self, key: str, now: float) -> None:
        """Remove expired requests from window."""
        if key not in self._requests:
            return
        
        cutoff = now - self.window_seconds
        while self._requests[key] and self._requests[key][0] < cutoff:
            self._requests[key].popleft()
    
    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check without consuming."""
        now = time.time()
        
        with self._lock:
            self._clean_old_requests(key, now)
            
            current_count = len(self._requests.get(key, []))
            remaining = max(0, self.limit - current_count)
            
            return RateLimitResult(
                allowed=remaining >= cost,
                remaining=remaining,
                limit=self.limit,
                reset_at=datetime.fromtimestamp(now + self.window_seconds),
            )
    
    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire quota."""
        now = time.time()
        
        with self._lock:
            if key not in self._requests:
                self._requests[key] = deque()
            
            self._clean_old_requests(key, now)
            
            current_count = len(self._requests[key])
            if current_count + cost > self.limit:
                # Find when oldest request expires
                if self._requests[key]:
                    retry_after = self._requests[key][0] + self.window_seconds - now
                else:
                    retry_after = self.window_seconds
                
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {key}",
                    retry_after=retry_after,
                )
            
            # Record requests
            for _ in range(cost):
                self._requests[key].append(now)
            
            remaining = self.limit - current_count - cost
            
            return RateLimitResult(
                allowed=True,
                remaining=remaining,
                limit=self.limit,
                reset_at=datetime.fromtimestamp(now + self.window_seconds),
            )
    
    def reset(self, key: str) -> None:
        """Reset quota for key."""
        with self._lock:
            if key in self._requests:
                del self._requests[key]


class TokenBucketLimiter(RateLimiter):
    """Token bucket rate limiter."""
    
    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        refill_interval: float = 1.0,
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.refill_interval = refill_interval
        self._buckets: Dict[str, Tuple[float, float]] = {}
        self._lock = threading.Lock()
    
    def _get_tokens(self, key: str) -> float:
        """Get current token count for key."""
        now = time.time()
        
        if key not in self._buckets:
            return float(self.capacity)
        
        tokens, last_update = self._buckets[key]
        elapsed = now - last_update
        refilled = (elapsed / self.refill_interval) * self.refill_rate
        
        return min(self.capacity, tokens + refilled)
    
    def check(self, key: str, cost: int = 1) -> RateLimitResult:
        """Check without consuming."""
        with self._lock:
            tokens = self._get_tokens(key)
            
            return RateLimitResult(
                allowed=tokens >= cost,
                remaining=int(tokens),
                limit=self.capacity,
            )
    
    def acquire(self, key: str, cost: int = 1) -> RateLimitResult:
        """Acquire tokens."""
        now = time.time()
        
        with self._lock:
            tokens = self._get_tokens(key)
            
            if tokens < cost:
                # Calculate when enough tokens will be available
                needed = cost - tokens
                retry_after = (needed / self.refill_rate) * self.refill_interval
                
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {key}",
                    retry_after=retry_after,
                )
            
            self._buckets[key] = (tokens - cost, now)
            
            return RateLimitResult(
                allowed=True,
                remaining=int(tokens - cost),
                limit=self.capacity,
            )
    
    def reset(self, key: str) -> None:
        """Reset bucket for key."""
        with self._lock:
            if key in self._buckets:
                del self._buckets[key]


class QuotaManager:
    """Manage multiple rate limits per key."""
    
    def __init__(self):
        self._limiters: Dict[str, RateLimiter] = {}
    
    def add_limiter(self, name: str, limiter: RateLimiter) -> None:
        """Add a named limiter."""
        self._limiters[name] = limiter
    
    def check_all(self, key: str, cost: int = 1) -> Dict[str, RateLimitResult]:
        """Check all limiters."""
        return {
            name: limiter.check(key, cost)
            for name, limiter in self._limiters.items()
        }
    
    def acquire_all(self, key: str, cost: int = 1) -> Dict[str, RateLimitResult]:
        """Acquire from all limiters (atomic)."""
        # First check all
        for name, limiter in self._limiters.items():
            result = limiter.check(key, cost)
            if not result.allowed:
                raise RateLimitExceeded(
                    f"Rate limit '{name}' exceeded for {key}",
                    retry_after=result.retry_after,
                )
        
        # Then acquire from all
        return {
            name: limiter.acquire(key, cost)
            for name, limiter in self._limiters.items()
        }


# Convenience functions
def create_limiter(
    algorithm: str = "sliding_window",
    limit: int = 100,
    window_seconds: int = 60,
    **kwargs,
) -> RateLimiter:
    """Create a rate limiter."""
    if algorithm == "fixed_window":
        return FixedWindowLimiter(limit, window_seconds)
    elif algorithm == "sliding_window":
        return SlidingWindowLimiter(limit, window_seconds)
    elif algorithm == "token_bucket":
        return TokenBucketLimiter(
            capacity=limit,
            refill_rate=kwargs.get("refill_rate", limit / window_seconds),
            refill_interval=kwargs.get("refill_interval", 1.0),
        )
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


__all__ = [
    # Core classes
    "RateLimiter",
    "FixedWindowLimiter",
    "SlidingWindowLimiter",
    "TokenBucketLimiter",
    "QuotaManager",
    # Data classes
    "RateLimitResult",
    # Exceptions
    "RateLimitExceeded",
    # Convenience
    "create_limiter",
]
