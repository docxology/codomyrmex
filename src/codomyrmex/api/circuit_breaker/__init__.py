"""API Circuit Breaker Module — resilience patterns for API calls."""

__version__ = "0.1.0"

from codomyrmex.exceptions import BulkheadFullError, CircuitOpenError

from .breaker import CircuitBreaker
from .bulkhead import Bulkhead
from .decorators import circuit_breaker, retry
from .models import CircuitBreakerConfig, CircuitState, CircuitStats
from .retry import RetryPolicy

__all__ = [
    "Bulkhead",
    "BulkheadFullError",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitOpenError",
    "CircuitState",
    "CircuitStats",
    "RetryPolicy",
    "circuit_breaker",
    "retry",
]
