"""
Base cache interface.
"""

from abc import ABC, abstractmethod
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

from .stats import CacheStats

logger = get_logger(__name__)


class Cache(ABC):
    """Abstract base class for cache implementations."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a key from the cache.

        Args:
            key: Cache key to delete

        Returns:
            True if deleted, False if key didn't exist
        """
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all entries from the cache.

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists
        """
        pass

    @property
    @abstractmethod
    def stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            CacheStats object
        """
        pass

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern.

        Args:
            pattern: Pattern to match (supports wildcards)

        Returns:
            Number of keys deleted
        """
        # Default implementation - override in subclasses for better performance
        keys_to_delete = []
        # This is a basic implementation - subclasses should override
        return 0


