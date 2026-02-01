"""
API Rate Limiter Module

Rate limiting for APIs and services.
"""

__version__ = "0.1.0"

import threading
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool
    remaining: int = 0
    reset_at: Optional[datetime] = None
    retry_after_seconds: float = 0.0
    
    def to_headers(self) -> Dict[str, str]:
        """Convert to HTTP headers."""
        return {
            "X-RateLimit-Remaining": str(self.remaining),
            "X-RateLimit-Reset": self.reset_at.isoformat() if self.reset_at else "",
            "Retry-After": str(int(self.retry_after_seconds)) if not self.allowed else "",
        }


class RateLimiter(ABC):
    """Base class for rate limiters."""
    
    @abstractmethod
    def is_allowed(self, key: str) -> RateLimitResult:
        """Check if request is allowed."""
        pass
    
    @abstractmethod
    def acquire(self, key: str) -> RateLimitResult:
        """Acquire a rate limit slot."""
        pass


class FixedWindowLimiter(RateLimiter):
    """
    Fixed window rate limiter.
    
    Usage:
        limiter = FixedWindowLimiter(limit=100, window_seconds=60)
        
        result = limiter.acquire("user:123")
        if result.allowed:
            # process request
        else:
            # retry after result.retry_after_seconds
    """
    
    def __init__(self, limit: int = 100, window_seconds: float = 60.0):
        self.limit = limit
        self.window_seconds = window_seconds
        self._windows: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def _get_window(self, key: str) -> Dict[str, Any]:
        """Get or create window for key."""
        now = time.time()
        window_start = int(now / self.window_seconds) * self.window_seconds
        
        if key not in self._windows or self._windows[key]["start"] != window_start:
            self._windows[key] = {
                "start": window_start,
                "count": 0,
            }
        
        return self._windows[key]
    
    def is_allowed(self, key: str) -> RateLimitResult:
        """Check if request would be allowed."""
        with self._lock:
            window = self._get_window(key)
            remaining = self.limit - window["count"]
            reset_at = datetime.fromtimestamp(window["start"] + self.window_seconds)
            
            return RateLimitResult(
                allowed=window["count"] < self.limit,
                remaining=max(0, remaining),
                reset_at=reset_at,
            )
    
    def acquire(self, key: str) -> RateLimitResult:
        """Acquire a request slot."""
        with self._lock:
            window = self._get_window(key)
            reset_at = datetime.fromtimestamp(window["start"] + self.window_seconds)
            
            if window["count"] >= self.limit:
                retry_after = (window["start"] + self.window_seconds) - time.time()
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_at=reset_at,
                    retry_after_seconds=max(0, retry_after),
                )
            
            window["count"] += 1
            remaining = self.limit - window["count"]
            
            return RateLimitResult(
                allowed=True,
                remaining=remaining,
                reset_at=reset_at,
            )


class TokenBucketLimiter(RateLimiter):
    """
    Token bucket rate limiter.
    
    Allows bursting up to bucket size, then refills tokens at steady rate.
    
    Usage:
        limiter = TokenBucketLimiter(capacity=100, refill_rate=10)  # 10 tokens/sec
        
        result = limiter.acquire("api:key")
    """
    
    def __init__(self, capacity: int = 100, refill_rate: float = 10.0):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self._buckets: Dict[str, Dict[str, float]] = {}
        self._lock = threading.Lock()
    
    def _get_bucket(self, key: str) -> Dict[str, float]:
        """Get or create bucket for key."""
        now = time.time()
        
        if key not in self._buckets:
            self._buckets[key] = {
                "tokens": float(self.capacity),
                "last_refill": now,
            }
        else:
            # Refill tokens
            bucket = self._buckets[key]
            elapsed = now - bucket["last_refill"]
            new_tokens = elapsed * self.refill_rate
            bucket["tokens"] = min(self.capacity, bucket["tokens"] + new_tokens)
            bucket["last_refill"] = now
        
        return self._buckets[key]
    
    def is_allowed(self, key: str) -> RateLimitResult:
        """Check if request would be allowed."""
        with self._lock:
            bucket = self._get_bucket(key)
            
            return RateLimitResult(
                allowed=bucket["tokens"] >= 1.0,
                remaining=int(bucket["tokens"]),
            )
    
    def acquire(self, key: str, cost: float = 1.0) -> RateLimitResult:
        """Acquire tokens from bucket."""
        with self._lock:
            bucket = self._get_bucket(key)
            
            if bucket["tokens"] < cost:
                # Calculate wait time
                tokens_needed = cost - bucket["tokens"]
                wait_time = tokens_needed / self.refill_rate
                
                return RateLimitResult(
                    allowed=False,
                    remaining=int(bucket["tokens"]),
                    retry_after_seconds=wait_time,
                )
            
            bucket["tokens"] -= cost
            
            return RateLimitResult(
                allowed=True,
                remaining=int(bucket["tokens"]),
            )


class SlidingWindowLimiter(RateLimiter):
    """
    Sliding window rate limiter.
    
    Smoother than fixed window, tracks requests over sliding time window.
    """
    
    def __init__(self, limit: int = 100, window_seconds: float = 60.0):
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = {}
        self._lock = threading.Lock()
    
    def _cleanup(self, key: str) -> None:
        """Remove old requests."""
        if key not in self._requests:
            return
        
        cutoff = time.time() - self.window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]
    
    def is_allowed(self, key: str) -> RateLimitResult:
        """Check if request would be allowed."""
        with self._lock:
            self._cleanup(key)
            count = len(self._requests.get(key, []))
            
            return RateLimitResult(
                allowed=count < self.limit,
                remaining=max(0, self.limit - count),
            )
    
    def acquire(self, key: str) -> RateLimitResult:
        """Acquire a request slot."""
        with self._lock:
            self._cleanup(key)
            
            if key not in self._requests:
                self._requests[key] = []
            
            if len(self._requests[key]) >= self.limit:
                oldest = self._requests[key][0]
                retry_after = oldest + self.window_seconds - time.time()
                
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    retry_after_seconds=max(0, retry_after),
                )
            
            self._requests[key].append(time.time())
            remaining = self.limit - len(self._requests[key])
            
            return RateLimitResult(
                allowed=True,
                remaining=remaining,
            )


class RateLimiterMiddleware:
    """
    Middleware for applying rate limits.
    
    Usage:
        limiter = RateLimiterMiddleware(
            FixedWindowLimiter(limit=100, window_seconds=60)
        )
        
        def get_key(request):
            return request.client_ip
        
        def handle_request(request):
            result = limiter.check(get_key(request))
            if not result.allowed:
                return {"error": "Rate limited"}, 429, result.to_headers()
            return process(request)
    """
    
    def __init__(self, limiter: RateLimiter):
        self.limiter = limiter
    
    def check(self, key: str) -> RateLimitResult:
        """Check and acquire rate limit."""
        return self.limiter.acquire(key)
    
    def would_allow(self, key: str) -> bool:
        """Check if request would be allowed without consuming."""
        return self.limiter.is_allowed(key).allowed


__all__ = [
    # Enums
    "RateLimitStrategy",
    # Data classes
    "RateLimitResult",
    # Limiters
    "RateLimiter",
    "FixedWindowLimiter",
    "TokenBucketLimiter",
    "SlidingWindowLimiter",
    # Middleware
    "RateLimiterMiddleware",
]
