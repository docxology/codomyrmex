"""
Soul Module

The soul module provides artificial consciousness, self-reflection, and personality management.
"""

from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class Soul:
    """Main class for soul functionality."""

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize Soul.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.personality = self.config.get("personality", "default")
        logger.info("Soul initialized")

    def process(self, data: Any) -> Any:
        """
        Process input data.

        Args:
            data: Input data to process.

        Returns:
            Processed data.

        Raises:
            NotImplementedError: As this is a base method needing implementation.
        """
        logger.debug(f"Processing data: {type(data).__name__}")
        raise NotImplementedError(
            "process() requires implementation by consuming module"
        )

    def reflect(self, query: str) -> str:
        """
        Perform self-reflection on a given query based on personality.

        Args:
            query: The query to reflect upon.

        Returns:
            A string representing the reflection.

        Raises:
            ValueError: If query is empty.
        """
        if not query:
            raise ValueError("Query cannot be empty.")
        logger.info(f"Soul reflecting on query: {query}")
        return f"Reflecting on '{query}' with personality '{self.personality}'."

    def get_personality(self) -> str:
        """
        Get the current personality of the soul.

        Returns:
            The current personality string.
        """
        return str(self.personality)


# Convenience function
def create_soul(config: dict[str, Any] | None = None) -> Soul:
    """
    Create a new Soul instance.

    Args:
        config: Optional configuration dictionary containing initialization parameters.

    Returns:
        An initialized Soul instance.
    """
    return Soul(config)
