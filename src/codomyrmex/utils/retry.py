"""Configurable retry decorator with backoff strategies.

Provides decorators and utilities for retrying failed operations
with exponential backoff, jitter, and configurable stop conditions.
"""

from __future__ import annotations

import asyncio
import functools
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)
F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,)


def _compute_delay(attempt: int, config: RetryConfig) -> float:
    """Compute delay for a given attempt number."""
    delay = config.base_delay * (config.exponential_base ** attempt)
    delay = min(delay, config.max_delay)
    if config.jitter:
        delay *= random.uniform(0.5, 1.5)
    return delay


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Decorator for retrying synchronous functions with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including first try).
        base_delay: Initial delay between retries in seconds.
        max_delay: Maximum delay cap in seconds.
        exponential_base: Base for exponential backoff calculation.
        jitter: Whether to add random jitter to delays.
        retryable_exceptions: Exception types that trigger a retry.

    Example:
        @retry(max_attempts=3, base_delay=0.5)
        def fetch_data(url: str) -> dict:
            return requests.get(url).json()
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions,
    )

    def decorator(func: F) -> F:
        """Decorator."""
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Wrapper."""
            last_exception: Exception | None = None
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    if attempt < config.max_attempts - 1:
                        delay = _compute_delay(attempt, config)
                        logger.warning(
                            "Retry %d/%d for %s after %.2fs: %s",
                            attempt + 1, config.max_attempts,
                            func.__name__, delay, e,
                        )
                        time.sleep(delay)
            raise last_exception  # type: ignore[misc]
        return wrapper  # type: ignore[return-value]
    return decorator


def async_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """Decorator for retrying async functions with exponential backoff."""
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions,
    )

    def decorator(func: Callable) -> Callable:
        """Decorator."""
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None
            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    if attempt < config.max_attempts - 1:
                        delay = _compute_delay(attempt, config)
                        logger.warning(
                            "Async retry %d/%d for %s after %.2fs: %s",
                            attempt + 1, config.max_attempts,
                            func.__name__, delay, e,
                        )
                        await asyncio.sleep(delay)
            raise last_exception  # type: ignore[misc]
        return wrapper
    return decorator
