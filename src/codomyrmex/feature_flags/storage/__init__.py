"""
Feature flag storage backends.

Provides an abstract FlagStore interface and two concrete implementations:
InMemoryFlagStore (for testing / ephemeral use) and FileFlagStore (for
simple JSON-file-based persistence).
"""

from __future__ import annotations

import json
import logging
import os
import threading
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class FlagStore(ABC):
    """Abstract base class for feature flag storage backends.

    All implementations must be safe for concurrent reads.  Write safety
    depends on the concrete backend.
    """

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Retrieve a flag value by key.

        Args:
            key: The flag identifier.

        Returns:
            The stored value, or None if the key does not exist.
        """

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Store or update a flag value.

        Args:
            key: The flag identifier.
            value: The value to persist (must be JSON-serialisable for
                   backends that persist to disk).
        """

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a flag by key.

        Args:
            key: The flag identifier.

        Returns:
            True if the key existed and was deleted, False otherwise.
        """

    @abstractmethod
    def list_all(self) -> dict[str, Any]:
        """Return a snapshot of all stored flags.

        Returns:
            A dictionary mapping flag keys to their values.
        """


class InMemoryFlagStore(FlagStore):
    """Thread-safe in-memory flag store.

    Suitable for testing, short-lived processes, or as a caching layer in
    front of a persistent backend.
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._data: dict[str, Any] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        """Return the requested value."""
        with self._lock:
            return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set the value."""
        with self._lock:
            self._data[key] = value

    def delete(self, key: str) -> bool:
        """Delete the specified resource."""
        with self._lock:
            if key in self._data:
                del self._data[key]
                return True
            return False

    def list_all(self) -> dict[str, Any]:
        """list All ."""
        with self._lock:
            return dict(self._data)

    def __len__(self) -> int:
        """len ."""
        with self._lock:
            return len(self._data)

    def __repr__(self) -> str:
        """repr ."""
        return f"InMemoryFlagStore(keys={list(self._data.keys())})"


class FileFlagStore(FlagStore):
    """JSON-file-backed flag store.

    Reads and writes a single JSON file.  Writes are atomic (write-to-temp
    then rename) to avoid corruption.  A threading lock serialises writes
    within the same process.

    Args:
        path: Filesystem path to the JSON storage file.  The file is
              created automatically if it does not exist.
    """

    def __init__(self, path: str) -> None:
        """Initialize this instance."""
        self._path = path
        self._lock = threading.Lock()
        if not os.path.exists(self._path):
            self._write({})

    # --- public interface ---

    def get(self, key: str) -> Any | None:
        """Return the requested value."""
        data = self._read()
        return data.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set the value."""
        with self._lock:
            data = self._read()
            data[key] = value
            self._write(data)

    def delete(self, key: str) -> bool:
        """Delete the specified resource."""
        with self._lock:
            data = self._read()
            if key in data:
                del data[key]
                self._write(data)
                return True
            return False

    def list_all(self) -> dict[str, Any]:
        """list All ."""
        return self._read()

    # --- internal helpers ---

    def _read(self) -> dict[str, Any]:
        """Load the JSON file; return empty dict on any read error."""
        try:
            with open(self._path, encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            return {}  # Valid: first-use, no flags file yet
        except json.JSONDecodeError as e:
            logger.warning("Feature flags storage file is corrupt, cannot parse JSON: %s", str(e))
            raise

    def _write(self, data: dict[str, Any]) -> None:
        """Atomically write *data* to the JSON file."""
        tmp_path = self._path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.write("\n")
        os.replace(tmp_path, self._path)

    def __repr__(self) -> str:
        """repr ."""
        return f"FileFlagStore(path={self._path!r})"


__all__ = [
    "FlagStore",
    "FileFlagStore",
    "InMemoryFlagStore",
]
