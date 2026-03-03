"""Crumb Cleaner Module.

Removes identifying metadata ("crumbs") from data structures to preserve privacy.
"""

from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class CrumbCleaner:
    """Sanitizes data by removing tracking crumbs and metadata."""

    def __init__(self) -> None:
        """Initialize CrumbCleaner with a default blacklist."""
        self._blacklist: set[str] = {
            "timestamp", "created_at", "updated_at",
            "ip_address", "device_id", "geo_lat", "geo_lon",
            "user_agent", "referrer", "cookie_id",
            "session_id", "trace_id", "crumb"
        }

    def scrub(self, data: Any) -> Any:
        """Recursively remove blacklisted keys from dictionaries and lists.

        Args:
            data: The dictionary, list, or primitive to scrub.

        Returns:
            A sanitized copy of the data.
        """
        if isinstance(data, dict):
            return {
                k: self.scrub(v)
                for k, v in data.items()
                if k.lower() not in self._blacklist
            }
        elif isinstance(data, list):
            return [self.scrub(item) for item in data]
        else:
            return data

    def generate_noise(self, size_bytes: int = 64) -> bytes:
        """Generate random noise to obscure activity patterns.

        Args:
            size_bytes: The number of random bytes to generate. Defaults to 64.

        Returns:
            A byte string of random noise.
        """
        import os
        return os.urandom(size_bytes)

    def configure_blacklist(self, add: list[str] | None = None, remove: list[str] | None = None) -> None:
        """Dynamically configure the metadata blacklist.

        Args:
            add: A list of keys to add to the blacklist.
            remove: A list of keys to remove from the blacklist.
        """
        if add:
            for key in add:
                self._blacklist.add(key.lower())
                logger.debug(f"Added to blacklist: {key}")

        if remove:
            for key in remove:
                if key.lower() in self._blacklist:
                    self._blacklist.remove(key.lower())
                    logger.debug(f"Removed from blacklist: {key}")
