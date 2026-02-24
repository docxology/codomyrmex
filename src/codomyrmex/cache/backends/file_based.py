"""
File-based cache backend.
"""

import json
import pickle
import tempfile
import time
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from ..cache import Cache
from ..stats import CacheStats

logger = get_logger(__name__)


class FileBasedCache(Cache):
    """File-based cache implementation."""

    def __init__(self, cache_dir: Path | None = None, default_ttl: int | None = None):
        """Initialize file-based cache.

        Args:
            cache_dir: Directory for cache files
            default_ttl: Default time-to-live in seconds
        """
        self.cache_dir = cache_dir or Path(tempfile.gettempdir()) / "codomyrmex_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self._stats = CacheStats()

    def _get_file_path(self, key: str) -> Path:
        """Get file path for a cache key."""
        import hashlib
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def _get_meta_path(self, key: str) -> Path:
        """Get metadata file path for a cache key."""
        import hashlib
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.meta"

    def get(self, key: str) -> Any | None:
        """Get a value from the cache."""
        self._stats.total_requests += 1

        file_path = self._get_file_path(key)
        meta_path = self._get_meta_path(key)

        if not file_path.exists() or not meta_path.exists():
            self._stats.misses += 1
            return None

        try:
            # Read metadata
            with open(meta_path) as f:
                meta = json.load(f)

            # Check expiration
            if meta.get("ttl") is not None:
                if time.time() - meta["timestamp"] > meta["ttl"]:
                    file_path.unlink(missing_ok=True)
                    meta_path.unlink(missing_ok=True)
                    self._stats.misses += 1
                    return None

            # Read value
            with open(file_path, "rb") as f:
                value = pickle.load(f)

            self._stats.hits += 1
            return value
        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            self._stats.misses += 1
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set a value in the cache."""
        file_path = self._get_file_path(key)
        meta_path = self._get_meta_path(key)

        try:
            # Write value
            with open(file_path, "wb") as f:
                pickle.dump(value, f)

            # Write metadata
            ttl = ttl or self.default_ttl
            meta = {
                "timestamp": time.time(),
                "ttl": ttl,
            }
            with open(meta_path, "w") as f:
                json.dump(meta, f)

            self._stats.size += 1
            return True
        except Exception as e:
            logger.error(f"Error writing cache: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete a key from the cache."""
        file_path = self._get_file_path(key)
        meta_path = self._get_meta_path(key)

        deleted = False
        if file_path.exists():
            file_path.unlink()
            deleted = True
        if meta_path.exists():
            meta_path.unlink()
            deleted = True

        if deleted:
            self._stats.size = max(0, self._stats.size - 1)

        return deleted

    def clear(self) -> bool:
        """Clear all entries from the cache."""
        try:
            for file_path in self.cache_dir.glob("*.cache"):
                file_path.unlink()
            for meta_path in self.cache_dir.glob("*.meta"):
                meta_path.unlink()
            self._stats.size = 0
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        file_path = self._get_file_path(key)
        meta_path = self._get_meta_path(key)

        if not file_path.exists() or not meta_path.exists():
            return False

        try:
            # Check expiration
            with open(meta_path) as f:
                meta = json.load(f)

            if meta.get("ttl") is not None:
                if time.time() - meta["timestamp"] > meta["ttl"]:
                    file_path.unlink(missing_ok=True)
                    meta_path.unlink(missing_ok=True)
                    return False

            return True
        except Exception:
            return False

    @property
    def stats(self) -> CacheStats:
        """Get cache statistics."""
        self._stats.size = len(list(self.cache_dir.glob("*.cache")))
        return self._stats



