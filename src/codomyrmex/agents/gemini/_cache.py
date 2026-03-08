"""Mixin for Gemini cached content operations."""

from typing import Any

from google.genai import types

from codomyrmex.agents.core.exceptions import GeminiError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GeminiCacheMixin:
    """Cached content creation, listing, retrieval, update, and deletion.

    Requires ``client`` from the host class.
    """

    def create_cached_content(
        self,
        model: str,
        contents: Any,
        ttl: str | None = None,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        """Create cached content for repeated use."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            config = types.CreateCachedContentConfig(
                contents=contents, ttl=ttl, display_name=display_name
            )
            return self.client.caches.create(
                model=model, config=config
            ).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to create cached content: %s", e)
            raise GeminiError(f"Failed to create cached content: {e}") from e

    def list_cached_contents(self) -> list[dict[str, Any]]:
        """List all cached contents."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return [c.model_dump() for c in self.client.caches.list()]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to list cached contents: %s", e)
            raise GeminiError(f"Failed to list cached contents: {e}") from e

    def get_cached_content(self, name: str) -> dict[str, Any]:
        """Get cached content by name."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.caches.get(name=name).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to get cached content %s: %s", name, e)
            raise GeminiError(f"Failed to get cached content {name}: {e}") from e

    def delete_cached_content(self, name: str) -> bool:
        """Delete cached content."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            self.client.caches.delete(name=name)
            return True
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to delete cached content %s: %s", name, e)
            raise GeminiError(f"Failed to delete cached content {name}: {e}") from e

    def update_cached_content(
        self, name: str, ttl: str | None = None
    ) -> dict[str, Any]:
        """Update cached content TTL."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            return self.client.caches.update(
                name=name, config=types.UpdateCachedContentConfig(ttl=ttl)
            ).model_dump()
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to update cached content %s: %s", name, e)
            raise GeminiError(f"Failed to update cached content {name}: {e}") from e
