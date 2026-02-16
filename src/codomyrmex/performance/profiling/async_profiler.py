"""Asynchronous function profiler."""

import functools
import logging
import time
from collections.abc import Callable

logger = logging.getLogger(__name__)

class AsyncProfiler:
    """Profiles asynchronous functions to identify bottlenecks."""

    @staticmethod
    def profile(func: Callable) -> Callable:
        """Decorator to profile an async function."""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                end_time = time.perf_counter()
                duration = end_time - start_time
                logger.info(f"Async Profile: {func.__name__} took {duration:.4f}s")
        return wrapper
