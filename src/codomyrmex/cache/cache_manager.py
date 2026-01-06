"""
Cache manager for multiple cache backends.
"""

from typing import Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

from .backends.file_based import FileBasedCache
from .backends.in_memory import InMemoryCache
from .cache import Cache

logger = get_logger(__name__)


class CacheManager:
    """Manager for cache instances."""

    def __init__(self):
        """Initialize cache manager."""
        self._caches: dict[str, Cache] = {}
        self._default_backend = "in_memory"

    def get_cache(self, name: str = "default", backend: Optional[str] = None) -> Cache:
        """Get a cache instance by name.

        Args:
            name: Cache name
            backend: Cache backend (in_memory, file_based, redis). If None, uses default.

        Returns:
            Cache instance
        """
        cache_key = f"{name}:{backend or self._default_backend}"
        if cache_key not in self._caches:
            backend = backend or self._default_backend
            if backend == "in_memory":
                self._caches[cache_key] = InMemoryCache()
            elif backend == "file_based":
                self._caches[cache_key] = FileBasedCache()
            elif backend == "redis":
                try:
                    from .backends.redis_backend import RedisCache
                    self._caches[cache_key] = RedisCache()
                except ImportError:
                    logger.warning("Redis not available, falling back to in-memory cache")
                    self._caches[cache_key] = InMemoryCache()
            else:
                logger.warning(f"Unknown backend {backend}, using in-memory cache")
                self._caches[cache_key] = InMemoryCache()

        return self._caches[cache_key]

