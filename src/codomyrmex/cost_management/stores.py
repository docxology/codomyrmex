"""
Cost Management Stores

Storage backends for cost entries.
"""

import json
import threading
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

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
        tags_filter: dict[str, str] | None = None,
    ) -> list[CostEntry]:
        """Get entries in date range with optional filtering."""
        pass


class InMemoryCostStore(CostStore):
    """In-memory cost storage."""

    def __init__(self) -> None:
        """Initialize in-memory cost store."""
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
        tags_filter: dict[str, str] | None = None,
    ) -> list[CostEntry]:
        """Get entries in date range with optional filtering."""
        results = []
        with self._lock:
            for entry in self._entries:
                if start <= entry.timestamp <= end:
                    if category is not None and entry.category != category:
                        continue

                    if tags_filter:
                        match = True
                        for k, v in tags_filter.items():
                            if entry.tags.get(k) != v:
                                match = False
                                break
                        if not match:
                            continue

                    results.append(entry)
        return results

    def get_all(self) -> list[CostEntry]:
        """Get all entries."""
        with self._lock:
            return list(self._entries)

    def clear(self) -> None:
        """Clear all entries."""
        with self._lock:
            self._entries.clear()


class JSONCostStore(CostStore):
    """Simple JSON file-based cost storage."""

    def __init__(self, filepath: str | Path) -> None:
        """Initialize JSON file-based cost store."""
        self.filepath = Path(filepath)
        self._lock = threading.Lock()
        if not self.filepath.exists():
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            self._save_to_file([])

    def _load_from_file(self) -> list[dict[str, Any]]:
        """Load entries from JSON file."""
        if not self.filepath.exists():
            return []
        try:
            with open(self.filepath, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_to_file(self, data: list[dict[str, Any]]) -> None:
        """Save entries to JSON file."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def save_entry(self, entry: CostEntry) -> None:
        """Save a cost entry."""
        with self._lock:
            entries = self._load_from_file()
            entries.append(entry.to_dict())
            self._save_to_file(entries)

    def get_entries(
        self,
        start: datetime,
        end: datetime,
        category: CostCategory | None = None,
        tags_filter: dict[str, str] | None = None,
    ) -> list[CostEntry]:
        """Get entries in date range with optional filtering."""
        with self._lock:
            raw_entries = self._load_from_file()
            entries = [CostEntry.from_dict(e) for e in raw_entries]

            results = []
            for entry in entries:
                if start <= entry.timestamp <= end:
                    if category is not None and entry.category != category:
                        continue

                    if tags_filter:
                        match = True
                        for k, v in tags_filter.items():
                            if entry.tags.get(k) != v:
                                match = False
                                break
                        if not match:
                            continue

                    results.append(entry)
            return results
