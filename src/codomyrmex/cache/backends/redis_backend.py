"""
Redis cache backend (optional).
"""

import json
import os
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from ..cache import Cache
from ..stats import CacheStats

logger = get_logger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisCache(Cache):
    """Redis cache implementation."""

    def __init__(self, host: str = "", port: int = 0, db: int = 0, default_ttl: int | None = None):
        """Initialize Redis cache.

        Args:
            host: Redis host (default from REDIS_HOST env or 'localhost')
            port: Redis port (default from REDIS_PORT env or 6379)
            db: Redis database number
            default_ttl: Default time-to-live in seconds
        """
        if not REDIS_AVAILABLE:
            raise ImportError("redis package not available. Install with: pip install redis")

        host = host or os.getenv("REDIS_HOST", "localhost")
        port = port or int(os.getenv("REDIS_PORT", "6379"))
        if not (1 <= port <= 65535):
            raise ValueError(f"Invalid Redis port: {port}. Must be between 1 and 65535.")
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=False)
        self.default_ttl = default_ttl
        self._stats = CacheStats()

    def get(self, key: str) -> Any | None:
        """Get a value from the cache."""
        self._stats.total_requests += 1

        try:
            value = self.client.get(key)
            if value is None:
                self._stats.misses += 1
                return None

            self._stats.hits += 1
            return json.loads(value.decode("utf-8"))  # SECURITY: JSON instead of pickle
        except Exception as e:
            logger.error(f"Error reading from Redis: {e}")
            self._stats.misses += 1
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set a value in the cache."""
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str).encode("utf-8")  # SECURITY: JSON instead of pickle
            if ttl:
                self.client.setex(key, ttl, serialized)
            else:
                self.client.set(key, serialized)
            self._stats.size += 1
            return True
        except Exception as e:
            logger.error(f"Error writing to Redis: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete a key from the cache."""
        try:
            result = self.client.delete(key)
            if result:
                self._stats.size = max(0, self._stats.size - 1)
            return bool(result)
        except Exception as e:
            logger.error(f"Error deleting from Redis: {e}")
            return False

    def clear(self) -> bool:
        """Clear all entries from the cache."""
        try:
            self.client.flushdb()
            self._stats.size = 0
            return True
        except Exception as e:
            logger.error(f"Error clearing Redis: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Error checking Redis: {e}")
            return False

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        try:
            info = self.client.info("stats")
            self._stats.hits = info.get("keyspace_hits", 0)
            self._stats.misses = info.get("keyspace_misses", 0)
            self._stats.total_requests = self._stats.hits + self._stats.misses
            self._stats.size = self.client.dbsize()
        except Exception as e:
            logger.warning("Failed to retrieve Redis cache stats: %s", e)
        return self._stats


