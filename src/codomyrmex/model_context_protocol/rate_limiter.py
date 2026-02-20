# DEPRECATED(v0.2.0): Shim module. Import from model_context_protocol.reliability.rate_limiter instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: model_context_protocol.reliability.rate_limiter"""
from .reliability.rate_limiter import *  # noqa: F401,F403
from .reliability.rate_limiter import (
    RateLimiter,
    RateLimiterConfig,
    _TokenBucket,
)
