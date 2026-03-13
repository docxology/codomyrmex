"""Hermes Gateway Identity Resolution.

Maps external platform identifiers (e.g., telegram:12345) to unified internal user profiles.
"""

import asyncio
import json
import uuid
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class IdentityResolver:
    """Async-safe global identity manager resolving external contacts into global users."""

    def __init__(self, file_path: str | Path | None = None) -> None:
        if file_path is None:
            self.file_path = Path.home() / ".codomyrmex" / "hermes" / "identities.json"
        else:
            self.file_path = Path(file_path)

        self._lock = asyncio.Lock()

        # internal_id -> {"name": "...", "platforms": {"telegram": "12345", "discord": "67890"}}
        self._profiles: dict[str, dict[str, Any]] = {}

    def _ensure_dir(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _read_disk(self) -> None:
        if not self.file_path.exists():
            return
        try:
            data = json.loads(self.file_path.read_text())
            if isinstance(data, dict):
                self._profiles = data
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse identities '{self.file_path}': {e}")

    def _write_disk(self) -> None:
        self._ensure_dir()
        self.file_path.write_text(json.dumps(self._profiles, indent=2))

    async def initialize(self) -> None:
        """Async init reading from disk."""
        async with self._lock:
            self._read_disk()
            logger.debug(f"Loaded {len(self._profiles)} global identity profiles.")

    async def resolve(
        self, platform: str, external_id: str, default_name: str = "Unknown"
    ) -> str:
        """Resolve a platform-specific ID to a global internal ID.

        If the external ID is completely unknown, generates a new global profile implicitly.
        """
        async with self._lock:
            self._read_disk()

            # Step 1: Does this mapping already exist anywhere?
            for internal_id, data in self._profiles.items():
                platforms = data.get("platforms", {})
                if platforms.get(platform) == external_id:
                    return internal_id

            # Step 2: It doesn't exist, generate a brand new universal profile
            new_internal_id = f"usr_{uuid.uuid4().hex[:12]}"
            self._profiles[new_internal_id] = {
                "name": default_name,
                "platforms": {platform: external_id},
            }
            self._write_disk()
            logger.info(
                f"Registered new global identity {new_internal_id} for {platform}:{external_id}"
            )
            return new_internal_id

    async def link_identity(
        self, internal_id: str, platform: str, external_id: str
    ) -> bool:
        """Explicitly link a new platform ID to an existing global profile."""
        async with self._lock:
            self._read_disk()
            if internal_id not in self._profiles:
                return False

            self._profiles[internal_id].setdefault("platforms", {})[platform] = (
                external_id
            )
            self._write_disk()
            logger.info(
                f"Linked {platform}:{external_id} to existing global {internal_id}"
            )
            return True
