"""
Agentic Memory Stores

Storage backends for the memory system.
"""

import json
import threading
from abc import ABC, abstractmethod

from .models import Memory


class MemoryStore(ABC):
    """Base class for memory storage backends."""

    @abstractmethod
    def save(self, memory: Memory) -> None:
        """Save a memory."""
        pass

    @abstractmethod
    def get(self, memory_id: str) -> Memory | None:
        """Get a memory by ID."""
        pass

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        pass

    @abstractmethod
    def list_all(self) -> list[Memory]:
        """List all memories."""
        pass


class InMemoryStore(MemoryStore):
    """In-memory storage for memories."""

    def __init__(self):
        self._memories: dict[str, Memory] = {}
        self._lock = threading.Lock()

    def save(self, memory: Memory) -> None:
        """Save a memory."""
        with self._lock:
            self._memories[memory.id] = memory

    def get(self, memory_id: str) -> Memory | None:
        """Get a memory by ID."""
        return self._memories.get(memory_id)

    def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        with self._lock:
            if memory_id in self._memories:
                del self._memories[memory_id]
                return True
        return False

    def list_all(self) -> list[Memory]:
        """List all memories."""
        with self._lock:
            return list(self._memories.values())


class JSONFileStore(MemoryStore):
    """JSON file storage for memories."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._memories: dict[str, Memory] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        """Load memories from file."""
        try:
            with open(self.file_path) as f:
                data = json.load(f)
                for item in data:
                    memory = Memory.from_dict(item)
                    self._memories[memory.id] = memory
        except (FileNotFoundError, json.JSONDecodeError):
            self._memories = {}

    def _save_to_file(self) -> None:
        """Save all memories to file."""
        data = [m.to_dict() for m in self._memories.values()]
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def save(self, memory: Memory) -> None:
        """Save a memory."""
        with self._lock:
            self._memories[memory.id] = memory
            self._save_to_file()

    def get(self, memory_id: str) -> Memory | None:
        """Get a memory by ID."""
        return self._memories.get(memory_id)

    def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        with self._lock:
            if memory_id in self._memories:
                del self._memories[memory_id]
                self._save_to_file()
                return True
        return False

    def list_all(self) -> list[Memory]:
        """List all memories."""
        with self._lock:
            return list(self._memories.values())
