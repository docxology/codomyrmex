"""Edge-cloud state synchronization."""

import threading
from typing import Any

from ..core.models import SyncState


class EdgeSynchronizer:
    """Synchronize state between edge and cloud."""

    def __init__(self):
        self._local_state: SyncState | None = None
        self._remote_version = 0
        self._pending_changes: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def get_local_state(self) -> SyncState | None:
        return self._local_state

    def update_local(self, data: dict[str, Any]) -> SyncState:
        """Update local state."""
        with self._lock:
            version = (self._local_state.version if self._local_state else 0) + 1
            self._local_state = SyncState.from_data(data, version)
            self._pending_changes.append({
                "type": "update",
                "version": version,
                "data": data,
            })
        return self._local_state

    def apply_remote(self, state: SyncState) -> bool:
        """Apply remote state if newer."""
        with self._lock:
            if not self._local_state or state.version > self._local_state.version:
                self._local_state = state
                self._remote_version = state.version
                return True
        return False

    def get_pending_changes(self) -> list[dict[str, Any]]:
        """Get changes to sync to remote."""
        with self._lock:
            changes = self._pending_changes.copy()
            return changes

    def confirm_sync(self, up_to_version: int) -> None:
        """Confirm changes synced."""
        with self._lock:
            self._pending_changes = [
                c for c in self._pending_changes if c["version"] > up_to_version
            ]
