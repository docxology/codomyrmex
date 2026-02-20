"""Key-value memory store with TTL support.

Provides persistent-style memory for agents with expiration.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class MemoryEntry:
    """A single memory entry.

    Attributes:
        key: Memory key.
        value: Stored value.
        created_at: Creation timestamp.
        expires_at: Expiry timestamp (0 = never).
        tags: Searchable tags.
        access_count: Number of reads.
    """

    key: str
    value: Any = None
    created_at: float = 0.0
    expires_at: float = 0.0
    tags: list[str] = field(default_factory=list)
    access_count: int = 0

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = time.time()

    @property
    def is_expired(self) -> bool:
        if self.expires_at == 0:
            return False
        return time.time() > self.expires_at


class MemoryStore:
    """Key-value memory store with TTL.

    Usage::

        store = MemoryStore()
        store.put("api_key", "sk-123", ttl=3600)
        val = store.get("api_key")
    """

    def __init__(self) -> None:
        self._entries: dict[str, MemoryEntry] = {}

    def put(self, key: str, value: Any, ttl: float = 0, tags: list[str] | None = None) -> None:
        """Store a value."""
        expires = time.time() + ttl if ttl > 0 else 0
        self._entries[key] = MemoryEntry(key=key, value=value, expires_at=expires, tags=tags or [])

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value."""
        entry = self._entries.get(key)
        if entry is None:
            return default
        if entry.is_expired:
            del self._entries[key]
            return default
        entry.access_count += 1
        return entry.value

    def delete(self, key: str) -> bool:
        return self._entries.pop(key, None) is not None

    def has(self, key: str) -> bool:
        entry = self._entries.get(key)
        if entry and entry.is_expired:
            del self._entries[key]
            return False
        return entry is not None

    def search_by_tag(self, tag: str) -> list[MemoryEntry]:
        self._clean_expired()
        return [e for e in self._entries.values() if tag in e.tags]

    @property
    def size(self) -> int:
        self._clean_expired()
        return len(self._entries)

    def keys(self) -> list[str]:
        self._clean_expired()
        return list(self._entries.keys())

    def _clean_expired(self) -> None:
        expired = [k for k, v in self._entries.items() if v.is_expired]
        for k in expired:
            del self._entries[k]


__all__ = ["MemoryEntry", "MemoryStore"]
