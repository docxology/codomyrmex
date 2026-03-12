"""Enhanced retry decorator with exponential backoff and jitter.

Production-grade retry logic with configurable exceptions, max attempts,
base delay, jitter, and callback hooks.

Example::

    @retry(max_attempts=3, base_delay=1.0)
    def flaky_api_call():
        response = requests.get("https://api.example.com/data")
        response.raise_for_status()
        return response.json()
"""

from __future__ import annotations

import functools
import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class RetryStats:
    """Statistics from a retry execution.

    Attributes:
        attempts: Number of attempts made.
        total_delay: Total time spent sleeping between retries.
        succeeded: Whether the final attempt succeeded.
        last_exception: The last exception encountered, if any.
    """

    attempts: int = 0
    total_delay: float = 0.0
    succeeded: bool = False
    last_exception: Exception | None = None


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[int, Exception, float], None] | None = None,
) -> Callable[[F], F]:
    """Decorator for retrying functions with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including first call).
        base_delay: Initial delay in seconds between retries.
        max_delay: Maximum delay cap in seconds.
        backoff_factor: Multiplier applied to delay after each retry.
        jitter: Whether to add random jitter to delay.
        retryable_exceptions: Tuple of exception types to retry on.
        on_retry: Optional callback ``(attempt, exception, delay)`` before retry.

    Returns:
        Decorated function.

    Example::

        @retry(max_attempts=5, base_delay=0.5, retryable_exceptions=(ConnectionError, TimeoutError))
        def fetch_data(url):
            return requests.get(url, timeout=10).json()
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay
            last_exc: Exception | None = None

            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    return result
                except retryable_exceptions as e:
                    last_exc = e
                    if attempt == max_attempts:
                        logger.error(
                            "All %d attempts failed for %s: %s",
                            max_attempts,
                            func.__name__,
                            e,
                        )
                        raise

                    actual_delay = min(delay, max_delay)
                    if jitter:
                        actual_delay *= 0.5 + random.random()

                    if on_retry:
                        on_retry(attempt, e, actual_delay)

                    logger.warning(
                        "Attempt %d/%d failed for %s: %s. Retrying in %.2fs...",
                        attempt,
                        max_attempts,
                        func.__name__,
                        e,
                        actual_delay,
                    )
                    time.sleep(actual_delay)
                    delay *= backoff_factor

            raise last_exc  # type: ignore[misc]

        wrapper._retry_config = {  # type: ignore[attr-defined]
            "max_attempts": max_attempts,
            "base_delay": base_delay,
            "max_delay": max_delay,
            "backoff_factor": backoff_factor,
            "jitter": jitter,
        }
        return wrapper  # type: ignore[return-value]

    return decorator


def retry_with_stats(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """Retry decorator that returns a ``(result, RetryStats)`` tuple.

    Args:
        max_attempts: Maximum attempts.
        base_delay: Initial delay.
        retryable_exceptions: Exceptions to retry on.

    Returns:
        Decorator that wraps return in ``(result, RetryStats)``.

    Example::

        @retry_with_stats(max_attempts=3)
        def unreliable():
            return 42

        result, stats = unreliable()
        print(f"Took {stats.attempts} attempts")
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> tuple[Any, RetryStats]:
            stats = RetryStats()
            delay = base_delay

            for attempt in range(1, max_attempts + 1):
                stats.attempts = attempt
                try:
                    result = func(*args, **kwargs)
                    stats.succeeded = True
                    return result, stats
                except retryable_exceptions as e:
                    stats.last_exception = e
                    if attempt == max_attempts:
                        raise
                    actual_delay = delay * (0.5 + random.random())
                    stats.total_delay += actual_delay
                    time.sleep(actual_delay)
                    delay *= 2.0

            msg = "Unreachable"
            raise RuntimeError(msg)

        return wrapper

    return decorator


__all__ = [
    "RetryStats",
    "retry",
    "retry_with_stats",
]
