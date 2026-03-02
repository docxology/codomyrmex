"""Memory stores — in-memory dict and JSON file-backed persistence.

Both stores expose the same CRUD surface: ``save``, ``get``, ``delete``,
``list_all``.  ``JSONFileStore`` is thread-safe via a ``threading.Lock``.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from codomyrmex.agentic_memory.models import Memory


class InMemoryStore:
    """In-process, dict-backed memory store."""

    def __init__(self) -> None:
        self._data: dict[str, Memory] = {}

    def save(self, memory: Memory) -> None:
        """Upsert a memory entry."""
        self._data[memory.id] = memory

    def get(self, memory_id: str) -> Memory | None:
        """Return a memory by id or ``None``."""
        mem = self._data.get(memory_id)
        if mem is not None:
            mem.access()
        return mem

    def delete(self, memory_id: str) -> bool:
        """Remove a memory. Returns ``True`` if it existed."""
        if memory_id in self._data:
            del self._data[memory_id]
            return True
        return False

    def list_all(self) -> list[Memory]:
        """Return every stored memory."""
        return list(self._data.values())


class JSONFileStore:
    """Thread-safe JSON file store that writes on every mutation.

    Each call to :meth:`save` / :meth:`delete` immediately flushes the
    full dataset to disk so concurrent-write tests pass.
    """

    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._lock = threading.Lock()
        self._data: dict[str, dict[str, Any]] = {}
        if self._path.exists():
            with open(self._path) as fh:
                raw = json.load(fh)
                if isinstance(raw, list):
                    for entry in raw:
                        self._data[entry["id"]] = entry
                elif isinstance(raw, dict):
                    self._data = raw

    # ── internal ─────────────────────────────────────────────────

    def _flush(self) -> None:
        """Flush."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as fh:
            json.dump(list(self._data.values()), fh, indent=2)

    # ── public API ───────────────────────────────────────────────

    def save(self, memory: Memory) -> None:
        """Save data to the specified destination."""
        with self._lock:
            self._data[memory.id] = memory.to_dict()
            self._flush()

    def get(self, memory_id: str) -> Memory | None:
        """Return the requested value."""
        with self._lock:
            raw = self._data.get(memory_id)
        if raw is None:
            return None
        return Memory.from_dict(raw)

    def delete(self, memory_id: str) -> bool:
        """Delete the specified resource."""
        with self._lock:
            if memory_id in self._data:
                del self._data[memory_id]
                self._flush()
                return True
            return False

    def list_all(self) -> list[Memory]:
        with self._lock:
            return [Memory.from_dict(v) for v in self._data.values()]
