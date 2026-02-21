"""Cache manager — multi-backend orchestration with namespacing and TTL defaults.

Provides:
- CacheManager: registry of named cache instances across backends
- Backend selection (in_memory, file_based, redis with auto-fallback)
- Default TTL configuration per cache
- List/remove/clear operations across all caches
- Summary statistics
"""

from __future__ import annotations

import time
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

from .backends.file_based import FileBasedCache
from .backends.in_memory import InMemoryCache
from .cache import Cache

logger = get_logger(__name__)


class CacheManager:
    """Manager for named cache instances across multiple backends.

    Example::

        mgr = CacheManager(default_ttl=300)
        cache = mgr.get_cache("sessions", backend="in_memory")
        cache.set("user_123", {"role": "admin"})
    """

    SUPPORTED_BACKENDS = ("in_memory", "file_based", "redis")

    def __init__(self, default_backend: str = "in_memory", default_ttl: float = 0) -> None:
        self._caches: dict[str, Cache] = {}
        self._backends: dict[str, str] = {}  # cache_key -> backend name
        self._default_backend = default_backend
        self._default_ttl = default_ttl
        self._created_at: dict[str, float] = {}

    def get_cache(self, name: str = "default", backend: str | None = None) -> Cache:
        """Get or create a cache instance by name.

        Args:
            name: Cache name.
            backend: Cache backend (in_memory, file_based, redis). Defaults to configured.

        Returns:
            Cache instance.
        """
        backend = backend or self._default_backend
        cache_key = f"{name}:{backend}"

        if cache_key not in self._caches:
            self._caches[cache_key] = self._create_backend(backend)
            self._backends[cache_key] = backend
            self._created_at[cache_key] = time.time()
            logger.info("Created cache '%s' with backend '%s'", name, backend)

        return self._caches[cache_key]

    def _create_backend(self, backend: str) -> Cache:
        """Create a cache backend instance."""
        if backend == "in_memory":
            return InMemoryCache()
        elif backend == "file_based":
            return FileBasedCache()
        elif backend == "redis":
            try:
                from .backends.redis_backend import RedisCache
                return RedisCache()
            except ImportError:
                logger.warning("Redis not available, falling back to in-memory cache")
                return InMemoryCache()
        else:
            logger.warning("Unknown backend %s, using in-memory cache", backend)
            return InMemoryCache()

    def has_cache(self, name: str) -> bool:
        """Check if a named cache exists."""
        return any(k.startswith(f"{name}:") for k in self._caches)

    def remove_cache(self, name: str) -> bool:
        """Remove a named cache (all backends)."""
        keys_to_remove = [k for k in self._caches if k.startswith(f"{name}:")]
        for key in keys_to_remove:
            del self._caches[key]
            self._backends.pop(key, None)
            self._created_at.pop(key, None)
        return len(keys_to_remove) > 0

    def list_caches(self) -> list[dict[str, Any]]:
        """List all active caches with their metadata."""
        return [
            {
                "key": key,
                "backend": self._backends.get(key, "unknown"),
                "created_at": self._created_at.get(key, 0),
            }
            for key in sorted(self._caches.keys())
        ]

    def clear_all(self) -> int:
        """Clear all caches. Returns number of caches cleared."""
        count = len(self._caches)
        for cache in self._caches.values():
            if hasattr(cache, "clear"):
                cache.clear()
        return count

    @property
    def cache_count(self) -> int:
        return len(self._caches)

    @property
    def default_backend(self) -> str:
        return self._default_backend

    def summary(self) -> dict[str, Any]:
        """Summary of all managed caches."""
        backends_used = set(self._backends.values())
        return {
            "total_caches": self.cache_count,
            "backends_used": sorted(backends_used),
            "default_backend": self._default_backend,
            "default_ttl": self._default_ttl,
        }
