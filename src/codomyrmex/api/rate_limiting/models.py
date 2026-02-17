"""
Rate Limiting Models

Data classes and exceptions for rate limiting.
"""

from dataclasses import dataclass
from datetime import datetime


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool
    remaining: int
    limit: int
    reset_at: datetime | None = None
    retry_after: float | None = None

    @property
    def headers(self) -> dict[str, str]:
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

    def to_headers(self) -> dict[str, str]:
        """Get rate limit headers (method alias for headers property)."""
        return self.headers
