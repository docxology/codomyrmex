"""Decorators: @circuit_breaker and @retry for function-level resilience."""

import functools
from collections.abc import Callable
from typing import TypeVar

from .breaker import CircuitBreaker
from .models import CircuitBreakerConfig
from .retry import RetryPolicy

T = TypeVar("T")


def circuit_breaker(
    name: str = "default",
    failure_threshold: int = 5,
    reset_timeout_s: float = 30.0,
) -> Callable:
    """Decorator wrapping a function with a circuit breaker."""
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        reset_timeout_s=reset_timeout_s,
    )
    breaker = CircuitBreaker(name=name, config=config)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            with breaker:
                return func(*args, **kwargs)

        wrapper.circuit_breaker = breaker
        return wrapper

    return decorator


def retry(
    max_retries: int = 3,
    backoff_base: float = 0.1,
    backoff_multiplier: float = 2.0,
    retryable_exceptions: tuple | None = None,
) -> Callable:
    """Decorator wrapping a function with retry logic and exponential backoff."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            policy = RetryPolicy(
                max_retries=max_retries,
                backoff_base=backoff_base,
                backoff_multiplier=backoff_multiplier,
                retryable_exceptions=retryable_exceptions,
            )

            last_exception: Exception | None = None

            for attempt in policy.attempts():
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if not policy.should_retry(e) or attempt >= max_retries:
                        raise

            if last_exception is not None:
                raise last_exception
            raise RuntimeError("Retry exhausted without capturing an exception")

        return wrapper

    return decorator
