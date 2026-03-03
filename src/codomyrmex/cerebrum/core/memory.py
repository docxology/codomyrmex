from typing import Any

from codomyrmex.logging_monitoring import get_logger

"""Working memory for short-term context storage."""

logger = get_logger(__name__)


class WorkingMemory:
    """Represents a short-term memory for storing reasoning context."""

    def __init__(self):
        """Initialize working memory."""
        self.storage: dict[str, Any] = {}
        self.logger = get_logger(__name__)

    def store(self, key: str, value: Any) -> None:
        """Store a value in memory.

        Args:
            key: Storage key
            value: Value to store
        """
        self.storage[key] = value
        self.logger.debug(f"Stored in memory: {key}")

    def retrieve(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from memory.

        Args:
            key: Storage key
            default: Default value if key not found

        Returns:
            Stored value or default
        """
        return self.storage.get(key, default)

    def delete(self, key: str) -> None:
        """Delete a value from memory.

        Args:
            key: Storage key
        """
        if key in self.storage:
            del self.storage[key]
            self.logger.debug(f"Deleted from memory: {key}")

    def clear(self) -> None:
        """Clear all memory."""
        self.storage.clear()
        self.logger.debug("Cleared working memory")

    def list_keys(self) -> list[str]:
        """List all keys in memory."""
        return list(self.storage.keys())

    def to_dict(self) -> dict[str, Any]:
        """Convert memory to dictionary."""
        return self.storage.copy()
