"""Decorator utilities for thin orchestration.

Provides ``retry``, ``timeout``, and ``condition`` helpers that wrap
callables with cross-cutting concerns (resilience, time-bounding,
conditional execution).

These were extracted from ``thin.py`` to keep each module focused.
"""

from __future__ import annotations

import asyncio
import inspect

from collections.abc import Callable

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

__all__ = [
    "condition",
    "retry",
    "timeout",
]


def retry(
    action: Callable, max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0
) -> Callable:
    """Wrap an action with retry logic.

    Args:
        action: Action to wrap
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier

    Returns:
        Wrapped action
    """

    async def wrapper(*args, **kwargs):
        last_error = None
        current_delay = delay

        for attempt in range(1, max_attempts + 1):
            try:
                if inspect.iscoroutinefunction(action):
                    return await action(*args, **kwargs)
                return action(*args, **kwargs)
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                last_error = e
                if attempt < max_attempts:
                    logger.warning(
                        "Attempt %s failed, retrying in %ss: %s",
                        attempt,
                        current_delay,
                        e,
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

        if last_error is not None:
            raise last_error
        raise RuntimeError("Retry exhausted without capturing an exception")

    return wrapper


def timeout(seconds: float) -> Callable:
    """Decorator to add timeout to an action.

    Args:
        seconds: Timeout in seconds

    Returns:
        Decorator function
    """

    def decorator(action):
        """Decorator."""

        async def wrapper(*args, **kwargs):
            if inspect.iscoroutinefunction(action):
                return await asyncio.wait_for(action(*args, **kwargs), timeout=seconds)
            loop = asyncio.get_event_loop()
            return await asyncio.wait_for(
                loop.run_in_executor(None, lambda: action(*args, **kwargs)),
                timeout=seconds,
            )

        return wrapper

    return decorator


def condition(predicate: Callable[[dict], bool]) -> Callable:
    """Create a condition function for conditional task execution.

    Args:
        predicate: Function that receives task results and returns bool

    Returns:
        Condition function
    """
    return predicate
