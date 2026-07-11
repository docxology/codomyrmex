"""Model context length registry."""

from __future__ import annotations

import json
import logging
import os
import shutil
import signal
import subprocess
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)

class ModelContextRegistry:
    """Dynamic context window resolution for OpenRouter models.

    Automatically resolves model context length capacities via the OpenRouter
    models.dev API. This means you no longer have to manually track if
    `qwen/qwen-2.5-72b-instruct` has 128K context limits; Hermes maps it
    instantly.

    When ContextCompressor experiences context pressure (>80% capacity),
    it accurately initiates token eviction based on this dynamic capacity map.

    Attributes:
        _cache: dict of model_id -> context_length (in tokens).
        _last_fetch: Timestamp of last API refresh.
        _ttl_seconds: Cache TTL before refresh.

    Example::

        registry = ModelContextRegistry()
        context_len = registry.get_context_length("qwen/qwen-2.5-72b-instruct")
        # Returns: 128000 (or cached value)
    """

    DEFAULT_CONTEXT_LENGTHS: dict[str, int] = {
        # Common models with known context windows
        "hermes3": 128_000,
        "llama3.1": 128_000,
        "llama3.1-70b": 128_000,
        "qwen2.5-72b": 128_000,
        "qwen2.5-72b-instruct": 128_000,
        "mixtral-8x22b": 64_000,
        "mixtral-8x7b": 32_000,
        "codestral": 32_000,
        "deepseek-coder-v2": 64_000,
        "phi3": 4_096,
        "gemma2-27b": 8_192,
    }

    def __init__(self, ttl_seconds: int = 3600) -> None:
        """Initialize the model context registry.

        Args:
            ttl_seconds: Time-to-live for cached context lengths (default 1 hour).
        """
        import threading

        self._cache: dict[str, int] = {}
        self._lock = threading.Lock()
        self._last_fetch: float | None = None
        self._ttl_seconds = ttl_seconds

    def get_context_length(self, model_id: str) -> int:
        """Get the context length for a model.

        Tries OpenRouter API first, falls back to known defaults.

        Args:
            model_id: OpenRouter model identifier.

        Returns:
            Context length in tokens.
        """
        # Check cache first
        with self._lock:
            if model_id in self._cache:
                return self._cache[model_id]

        # Try OpenRouter API
        context_len = self._fetch_from_openrouter(model_id)
        if context_len > 0:
            with self._lock:
                self._cache[model_id] = context_len
            return context_len

        # Fall back to known defaults (fuzzy match on model family)
        context_len = self._get_fallback_context(model_id)
        with self._lock:
            self._cache[model_id] = context_len
        return context_len

    def _fetch_from_openrouter(self, model_id: str) -> int:
        """Fetch context length from OpenRouter API.

        Args:
            model_id: Model identifier to query.

        Returns:
            Context length or 0 if not found.
        """
        import urllib.error
        import urllib.request

        try:
            url = f"https://openrouter.ai/api/v1/models/{model_id}"
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as response:
                import json

                data = json.loads(response.read().decode())
                context = data.get("data", {}).get("context_length")
                if context and isinstance(context, int):
                    logger.info(
                        "Resolved context length for %s: %d tokens",
                        model_id,
                        context,
                    )
                    return context
        except urllib.error.HTTPError as e:
            if e.code == 404:
                logger.debug("Model %s not found in OpenRouter registry", model_id)
        except Exception as exc:
            logger.debug("Failed to fetch context for %s: %s", model_id, exc)

        return 0

    def _get_fallback_context(self, model_id: str) -> int:
        """Get fallback context length from known defaults.

        Performs fuzzy matching on model family name.

        Args:
            model_id: Model identifier.

        Returns:
            Context length in tokens, or 128000 as safe default.
        """
        model_lower = model_id.lower()

        # Exact match
        if model_lower in self.DEFAULT_CONTEXT_LENGTHS:
            return self.DEFAULT_CONTEXT_LENGTHS[model_lower]

        # Fuzzy match on model family
        for known, length in self.DEFAULT_CONTEXT_LENGTHS.items():
            if known in model_lower:
                return length

        # Default safe context length for unknown models
        logger.warning(
            "Unknown model %s, defaulting to 128K context",
            model_id,
        )
        return 128_000

    def get_context_length_safe(self, model_id: str) -> int:
        """Thread-safe get_context_length with proper locking.

        Args:
            model_id: Model identifier.

        Returns:
            Context length in tokens.
        """
        with self._lock:
            if model_id in self._cache:
                return self._cache[model_id]

        # Fetch outside lock to avoid blocking
        context_len = self._fetch_from_openrouter(model_id)
        if context_len > 0:
            with self._lock:
                self._cache[model_id] = context_len
            return context_len

        # Fall back to known defaults
        context_len = self._get_fallback_context(model_id)
        with self._lock:
            self._cache[model_id] = context_len
        return context_len

    def is_stale(self) -> bool:
        """Check if the cache is stale and needs refresh.

        Returns:
            True if cache should be refreshed.
        """
        import time

        if self._last_fetch is None:
            return True
        return (time.time() - self._last_fetch) > self._ttl_seconds

    def clear_cache(self) -> None:
        """Clear the context length cache."""
        with self._lock:
            self._cache.clear()
            self._last_fetch = None


_model_context_registry: ModelContextRegistry | None = None


def get_model_context_registry() -> ModelContextRegistry:
    """Return the global ``ModelContextRegistry`` singleton."""
    global _model_context_registry
    if _model_context_registry is None:
        _model_context_registry = ModelContextRegistry()
    return _model_context_registry
