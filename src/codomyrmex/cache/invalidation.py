"""Cache invalidation strategies.

Provides TTL-based, event-driven, tag-based, and pattern-based
cache invalidation mechanisms.
"""

from __future__ import annotations

import fnmatch
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


class InvalidationStrategy(Enum):
    """Supported invalidation strategies."""
    TTL = "ttl"
    EVENT = "event"
    TAG = "tag"
    PATTERN = "pattern"
    MANUAL = "manual"


@dataclass
class CacheEntry:
    """Metadata about a cached item."""
    key: str
    created_at: float = field(default_factory=time.time)
    ttl_seconds: float | None = None
    tags: set[str] = field(default_factory=set)
    version: int = 1

    @property
    def is_expired(self) -> bool:
        if self.ttl_seconds is None:
            return False
        return (time.time() - self.created_at) > self.ttl_seconds


class InvalidationManager:
    """Manages cache invalidation across multiple strategies.

    Supports TTL expiration, tag-based bulk invalidation,
    pattern-based key matching, and event-driven invalidation.
    """

    def __init__(self) -> None:
        self._entries: dict[str, CacheEntry] = {}
        self._tag_index: dict[str, set[str]] = {}
        self._event_handlers: dict[str, list[Callable[[str], None]]] = {}
        self._invalidation_callbacks: list[Callable[[list[str]], None]] = []

    def register(self, key: str, ttl_seconds: float | None = None,
                 tags: set[str] | None = None) -> CacheEntry:
        """Register a cache entry for invalidation tracking."""
        entry = CacheEntry(key=key, ttl_seconds=ttl_seconds, tags=tags or set())
        self._entries[key] = entry
        for tag in entry.tags:
            self._tag_index.setdefault(tag, set()).add(key)
        return entry

    def check_expired(self) -> list[str]:
        """Check and return all TTL-expired keys."""
        expired = [k for k, e in self._entries.items() if e.is_expired]
        if expired:
            self._invalidate_keys(expired)
        return expired

    def invalidate_by_tag(self, tag: str) -> list[str]:
        """Invalidate all entries with a given tag."""
        keys = list(self._tag_index.get(tag, set()))
        self._invalidate_keys(keys)
        return keys

    def invalidate_by_pattern(self, pattern: str) -> list[str]:
        """Invalidate all entries whose key matches a glob pattern."""
        keys = [k for k in self._entries if fnmatch.fnmatch(k, pattern)]
        self._invalidate_keys(keys)
        return keys

    def invalidate_key(self, key: str) -> bool:
        """Invalidate a single key."""
        if key in self._entries:
            self._invalidate_keys([key])
            return True
        return False

    def on_event(self, event_type: str, handler: Callable[[str], None]) -> None:
        """Register a handler for event-driven invalidation."""
        self._event_handlers.setdefault(event_type, []).append(handler)

    def fire_event(self, event_type: str, context: str = "") -> None:
        """Fire an invalidation event."""
        for handler in self._event_handlers.get(event_type, []):
            try:
                handler(context)
            except Exception as e:
                logger.error("Invalidation event handler failed: %s", e)

    def on_invalidation(self, callback: Callable[[list[str]], None]) -> None:
        """Register a callback for when keys are invalidated."""
        self._invalidation_callbacks.append(callback)

    def _invalidate_keys(self, keys: list[str]) -> None:
        """Remove keys and notify callbacks."""
        for key in keys:
            entry = self._entries.pop(key, None)
            if entry:
                for tag in entry.tags:
                    self._tag_index.get(tag, set()).discard(key)
        if keys and self._invalidation_callbacks:
            for cb in self._invalidation_callbacks:
                try:
                    cb(keys)
                except Exception as e:
                    logger.error("Invalidation callback failed: %s", e)

    @property
    def tracked_count(self) -> int:
        return len(self._entries)
