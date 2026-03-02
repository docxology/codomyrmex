"""TTL manager for periodic cache cleanup."""

import threading
import time
from typing import Any
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class TTLManager:
    """Periodically cleans up expired keys from a cache."""

    def __init__(self, cleanup_interval: int = 60):
        self.cleanup_interval = cleanup_interval
        self._cache_registry: set[Any] = set()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def register_cache(self, cache: Any):
        """Register a cache instance for periodic cleanup."""
        self._cache_registry.add(cache)
        if self._thread is None:
            self.start()

    def start(self):
        """Start the cleanup thread."""
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the cleanup thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _run(self):
        """Run the operation."""
        while not self._stop_event.is_set():
            time.sleep(self.cleanup_interval)
            self.cleanup()

    def cleanup(self):
        """Trigger cleanup on all registered caches."""
        for cache in self._cache_registry:
            try:
                if hasattr(cache, "cleanup_expired"):
                    cache.cleanup_expired()
                elif hasattr(cache, "delete_pattern"):
                    # Fallback or specific logic
                    pass
            except Exception as e:
                logger.error(f"Error during cache cleanup: {e}")
