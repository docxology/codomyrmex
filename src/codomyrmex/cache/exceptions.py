"""Cache Exception Classes.

This module defines exceptions specific to cache operations including
storage, retrieval, expiration, and connection handling.
All exceptions inherit from CodomyrmexError for consistent error handling.
"""

from typing import Any

from codomyrmex.exceptions import CodomyrmexError


class CacheError(CodomyrmexError):
    """Base exception for cache-related errors.

    Attributes:
        message: Error description.
        cache_name: Name of the cache involved.
        backend: Cache backend type (e.g., 'redis', 'memory', 'file').
    """

    def __init__(
        self,
        message: str,
        cache_name: str | None = None,
        backend: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if cache_name:
            self.context["cache_name"] = cache_name
        if backend:
            self.context["backend"] = backend


class CacheExpiredError(CacheError):
    """Raised when attempting to access an expired cache entry.

    Attributes:
        message: Error description.
        key: The cache key that expired.
        expired_at: Timestamp when the entry expired.
        ttl: Original time-to-live value.
    """

    def __init__(
        self,
        message: str,
        key: str | None = None,
        expired_at: float | None = None,
        ttl: float | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if key:
            self.context["key"] = key
        if expired_at is not None:
            self.context["expired_at"] = expired_at
        if ttl is not None:
            self.context["ttl"] = ttl


class CacheFullError(CacheError):
    """Raised when cache storage is full and cannot accept new entries.

    Attributes:
        message: Error description.
        max_size: Maximum cache size.
        current_size: Current cache size.
        required_space: Space needed for the new entry.
    """

    def __init__(
        self,
        message: str,
        max_size: int | None = None,
        current_size: int | None = None,
        required_space: int | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if max_size is not None:
            self.context["max_size"] = max_size
        if current_size is not None:
            self.context["current_size"] = current_size
        if required_space is not None:
            self.context["required_space"] = required_space


class CacheConnectionError(CacheError):
    """Raised when connection to cache backend fails.

    Attributes:
        message: Error description.
        host: Cache server host.
        port: Cache server port.
        connection_timeout: Connection timeout in seconds.
    """

    def __init__(
        self,
        message: str,
        host: str | None = None,
        port: int | None = None,
        connection_timeout: float | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if host:
            self.context["host"] = host
        if port is not None:
            self.context["port"] = port
        if connection_timeout is not None:
            self.context["connection_timeout"] = connection_timeout


class CacheKeyError(CacheError):
    """Raised when a cache key is invalid or not found.

    Attributes:
        message: Error description.
        key: The problematic cache key.
        reason: Reason why the key is invalid.
    """

    def __init__(
        self,
        message: str,
        key: str | None = None,
        reason: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if key:
            self.context["key"] = key
        if reason:
            self.context["reason"] = reason


class CacheSerializationError(CacheError):
    """Raised when cache value serialization or deserialization fails.

    Attributes:
        message: Error description.
        key: The cache key being processed.
        value_type: Type of the value that failed to serialize.
    """

    def __init__(
        self,
        message: str,
        key: str | None = None,
        value_type: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if key:
            self.context["key"] = key
        if value_type:
            self.context["value_type"] = value_type


class CacheInvalidationError(CacheError):
    """Raised when cache invalidation fails.

    Attributes:
        message: Error description.
        pattern: The invalidation pattern that failed.
        keys_affected: Number of keys that should have been invalidated.
    """

    def __init__(
        self,
        message: str,
        pattern: str | None = None,
        keys_affected: int | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if pattern:
            self.context["pattern"] = pattern
        if keys_affected is not None:
            self.context["keys_affected"] = keys_affected
