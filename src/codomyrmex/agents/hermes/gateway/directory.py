"""Hermes Gateway channel directory routing.

Manages dynamic JSON syncing for external platforms discovering new group/DM endpoints natively.
"""

import asyncio
import json
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class ChannelDirectorySync:
    """Async-safe directory state manager."""

    def __init__(self, file_path: str | Path | None = None) -> None:
        if file_path is None:
            self.file_path = (
                Path.home() / ".codomyrmex" / "hermes" / "channel_directory.json"
            )
        else:
            self.file_path = Path(file_path)

        self._lock = asyncio.Lock()
        # Type: platform -> user_id -> metadata dict
        self._directory: dict[str, dict[str, dict[str, str]]] = {}

    def _ensure_dir(self) -> None:
        """Ensure parent directories exist."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _read_disk(self) -> None:
        """Read state from disk, ignoring if empty."""
        if not self.file_path.exists():
            return

        try:
            data = json.loads(self.file_path.read_text())
            if isinstance(data, dict):
                self._directory = data
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse channel directory '{self.file_path}': {e}")

    def _write_disk(self) -> None:
        """Flush memory state to disk."""
        self._ensure_dir()
        self.file_path.write_text(json.dumps(self._directory, indent=2))

    async def initialize(self) -> None:
        """Async init reading from disk."""
        async with self._lock:
            self._read_disk()
            logger.debug(f"Loaded channel sync tree with {len(self._directory)} items.")

    async def register_channel(
        self, platform: str, user_id: str, metadata: dict[str, str] | None = None
    ) -> None:
        """Safely register a new incoming platform channel mapping."""
        # Ensure metadata is never None - use empty dict as fallback
        safe_metadata: dict[str, str] = metadata if metadata is not None else {}

        async with self._lock:
            # Memory sync - ensure platform key exists with proper typing
            if platform not in self._directory:
                self._directory[platform] = {}
            # Assign metadata dict - type accepts dict[str, dict[str, str]]
            self._directory[platform][user_id] = safe_metadata

            # Flush
            self._write_disk()
            logger.info(f"Directory Sync: registered {platform} → {user_id}")

    async def get_directory(self) -> dict[str, dict[str, dict[str, str]]]:
        """Return a copy of the current synced routing tree."""
        async with self._lock:
            # Read to ensure we have any out-of-band updates before returning memory copy
            self._read_disk()
            import copy

            return copy.deepcopy(self._directory)
