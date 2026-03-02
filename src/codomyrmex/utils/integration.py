"""
Cross-Module Integration Utilities

Common patterns for integrating new modules.
"""

import asyncio
import functools
import logging
import time
from collections.abc import Callable
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypeVar

T = TypeVar('T')

# Module-level logger
logger = logging.getLogger("codomyrmex.integration")


# ============================================================================
# Logging Utilities
# ============================================================================

def setup_module_logging(
    module_name: str,
    level: int = logging.INFO,
    format_str: str | None = None,
) -> logging.Logger:
    """Set up logging for a module."""
    log = logging.getLogger(f"codomyrmex.{module_name}")
    log.setLevel(level)

    if not log.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        fmt = format_str or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        log.addHandler(handler)

    return log


def log_performance(
    operation: str,
    logger: logging.Logger | None = None,
):
    """Decorator to log function performance."""
    def decorator(func: Callable) -> Callable:
        """decorator ."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """wrapper ."""
            log = logger or logging.getLogger("codomyrmex")
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.time() - start) * 1000
                log.debug(f"{operation}: {elapsed:.2f}ms")
                return result
            except Exception as e:
                elapsed = (time.time() - start) * 1000
                log.error(f"{operation} failed after {elapsed:.2f}ms: {e}")
                raise
        return wrapper
    return decorator


# ============================================================================
# Async Helpers
# ============================================================================

def run_async(coro):
    """Run an async function from sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create new loop in thread for nested async
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


async def gather_with_concurrency(
    coroutines: list,
    max_concurrent: int = 10,
):
    """Run coroutines with limited concurrency."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*[limited(c) for c in coroutines])


def make_async(func: Callable) -> Callable:
    """Convert sync function to async."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper


# ============================================================================
# Retry Logic
# ============================================================================

@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    max_attempts: int = 3
    initial_delay: float = 0.1
    max_delay: float = 10.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple = (Exception,)


def with_retry(config: RetryConfig | None = None):
    """Decorator for retry logic with exponential backoff."""
    cfg = config or RetryConfig()

    def decorator(func: Callable) -> Callable:
        """decorator ."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """wrapper ."""
            import random
            last_exception = None
            delay = cfg.initial_delay

            for attempt in range(cfg.max_attempts):
                try:
                    return func(*args, **kwargs)
                except cfg.retryable_exceptions as e:
                    last_exception = e
                    if attempt < cfg.max_attempts - 1:
                        if cfg.jitter:
                            delay *= (1 + random.random() * 0.1)
                        time.sleep(min(delay, cfg.max_delay))
                        delay *= cfg.exponential_base

            raise last_exception
        return wrapper
    return decorator


async def async_retry(
    coro_func: Callable,
    *args,
    config: RetryConfig | None = None,
    **kwargs,
):
    """Async retry with exponential backoff."""
    import random
    cfg = config or RetryConfig()
    last_exception = None
    delay = cfg.initial_delay

    for attempt in range(cfg.max_attempts):
        try:
            return await coro_func(*args, **kwargs)
        except cfg.retryable_exceptions as e:
            last_exception = e
            if attempt < cfg.max_attempts - 1:
                if cfg.jitter:
                    delay *= (1 + random.random() * 0.1)
                await asyncio.sleep(min(delay, cfg.max_delay))
                delay *= cfg.exponential_base

    raise last_exception


# ============================================================================
# Resource Management
# ============================================================================

@contextmanager
def timed_operation(name: str, logger: logging.Logger | None = None):
    """Context manager for timing operations."""
    log = logger or logging.getLogger("codomyrmex")
    start = time.time()
    try:
        yield
    finally:
        elapsed = (time.time() - start) * 1000
        log.info(f"{name}: {elapsed:.2f}ms")


@asynccontextmanager
async def async_timed_operation(name: str, logger: logging.Logger | None = None):
    """Async context manager for timing operations."""
    log = logger or logging.getLogger("codomyrmex")
    start = time.time()
    try:
        yield
    finally:
        elapsed = (time.time() - start) * 1000
        log.info(f"{name}: {elapsed:.2f}ms")


# ============================================================================
# Module Registry
# ============================================================================

class ModuleRegistry:
    """Registry for cross-module integration."""

    _instance = None

    def __new__(cls):
        """new ."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._modules = {}
            cls._instance._hooks = {}
        return cls._instance

    def register(self, name: str, module: Any) -> None:
        """Register a module."""
        self._modules[name] = module

    def get(self, name: str) -> Any | None:
        """Get a registered module."""
        return self._modules.get(name)

    def add_hook(self, event: str, handler: Callable) -> None:
        """Add an event hook."""
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(handler)

    def trigger(self, event: str, *args, **kwargs) -> list[Any]:
        """Trigger all handlers for an event."""
        results = []
        for handler in self._hooks.get(event, []):
            try:
                results.append(handler(*args, **kwargs))
            except Exception as e:
                logger.error(f"Hook error for {event}: {e}")
        return results


# Singleton instance
registry = ModuleRegistry()


# ============================================================================
# Health Checking
# ============================================================================

@dataclass
class HealthStatus:
    """Health check result."""
    healthy: bool
    name: str
    message: str = ""
    latency_ms: float = 0.0
    checked_at: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """Aggregate health checks for modules."""

    def __init__(self):
        """Initialize this instance."""
        self._checks: dict[str, Callable[[], HealthStatus]] = {}

    def register(self, name: str, check_fn: Callable[[], HealthStatus]) -> None:
        """Register a health check."""
        self._checks[name] = check_fn

    def check_all(self) -> dict[str, HealthStatus]:
        """Run all health checks."""
        results = {}
        for name, check_fn in self._checks.items():
            start = time.time()
            try:
                status = check_fn()
                status.latency_ms = (time.time() - start) * 1000
                results[name] = status
            except Exception as e:
                results[name] = HealthStatus(
                    healthy=False,
                    name=name,
                    message=str(e),
                    latency_ms=(time.time() - start) * 1000,
                )
        return results

    def is_healthy(self) -> bool:
        """Check if all services are healthy."""
        return all(s.healthy for s in self.check_all().values())


__all__ = [
    # Logging
    "setup_module_logging",
    "log_performance",
    # Async
    "run_async",
    "gather_with_concurrency",
    "make_async",
    # Retry
    "RetryConfig",
    "with_retry",
    "async_retry",
    # Resources
    "timed_operation",
    "async_timed_operation",
    # Registry
    "ModuleRegistry",
    "registry",
    # Health
    "HealthChecker",
    "HealthStatus",
]
