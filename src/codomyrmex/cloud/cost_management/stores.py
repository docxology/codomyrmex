"""
Cost Management Stores

Storage backends for cost entries.
"""

import threading
from abc import ABC, abstractmethod
from datetime import datetime

from .models import CostCategory, CostEntry


class CostStore(ABC):
    """Base class for cost storage."""

    @abstractmethod
    def save_entry(self, entry: CostEntry) -> None:
        """Save a cost entry."""
        pass

    @abstractmethod
    def get_entries(
        self,
        start: datetime,
        end: datetime,
        category: CostCategory | None = None,
    ) -> list[CostEntry]:
        """Get entries in date range."""
        pass


class InMemoryCostStore(CostStore):
    """In-memory cost storage."""

    def __init__(self):
        """Initialize this instance."""
        self._entries: list[CostEntry] = []
        self._lock = threading.Lock()

    def save_entry(self, entry: CostEntry) -> None:
        """Save a cost entry."""
        with self._lock:
            self._entries.append(entry)

    def get_entries(
        self,
        start: datetime,
        end: datetime,
        category: CostCategory | None = None,
    ) -> list[CostEntry]:
        """Get entries in date range."""
        results = []
        for entry in self._entries:
            if start <= entry.timestamp <= end:
                if category is None or entry.category == category:
                    results.append(entry)
        return results

    def get_all(self) -> list[CostEntry]:
        """Get all entries."""
        return list(self._entries)

    def clear(self) -> None:
        """Clear all entries."""
        with self._lock:
            self._entries.clear()
