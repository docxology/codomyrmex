"""Edge-cloud state synchronization with conflict resolution and batching.

Provides:
- EdgeSynchronizer: bidirectional state sync between edge and cloud
- Conflict detection and resolution strategies
- Batch pending changes with size limits
- Sync history tracking
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..core.models import SyncState


class ConflictStrategy(Enum):
    """How to resolve version conflicts."""
    REMOTE_WINS = "remote_wins"
    LOCAL_WINS = "local_wins"
    LATEST_WINS = "latest_wins"


@dataclass
class SyncEvent:
    """Record of a sync operation."""
    direction: str  # "push" or "pull"
    version: int
    success: bool
    timestamp: float = field(default_factory=time.time)
    error: str = ""


class EdgeSynchronizer:
    """Synchronize state between edge and cloud.

    Supports bidirectional sync with configurable conflict resolution,
    change batching, and sync history tracking.

    Example::

        sync = EdgeSynchronizer(conflict_strategy=ConflictStrategy.REMOTE_WINS)
        sync.update_local({"temperature": 72.5})
        pending = sync.get_pending_changes()
    """

    def __init__(
        self,
        conflict_strategy: ConflictStrategy = ConflictStrategy.REMOTE_WINS,
        max_pending: int = 100,
    ) -> None:
        self._local_state: SyncState | None = None
        self._remote_version = 0
        self._pending_changes: list[dict[str, Any]] = []
        self._lock = threading.Lock()
        self._conflict_strategy = conflict_strategy
        self._max_pending = max_pending
        self._history: list[SyncEvent] = []

    @property
    def local_version(self) -> int:
        return self._local_state.version if self._local_state else 0

    @property
    def remote_version(self) -> int:
        return self._remote_version

    @property
    def pending_count(self) -> int:
        return len(self._pending_changes)

    @property
    def is_synced(self) -> bool:
        return self.pending_count == 0 and self.local_version == self._remote_version

    def get_local_state(self) -> SyncState | None:
        return self._local_state

    def update_local(self, data: dict[str, Any]) -> SyncState:
        """Update local state and queue a change for sync."""
        with self._lock:
            version = (self._local_state.version if self._local_state else 0) + 1
            self._local_state = SyncState.from_data(data, version)
            self._pending_changes.append({
                "type": "update",
                "version": version,
                "data": data,
                "timestamp": time.time(),
            })
            # Trim oldest if over max
            if len(self._pending_changes) > self._max_pending:
                self._pending_changes = self._pending_changes[-self._max_pending:]
        return self._local_state

    def apply_remote(self, state: SyncState) -> bool:
        """Apply remote state using the configured conflict strategy."""
        with self._lock:
            should_apply = False
            if not self._local_state:
                should_apply = True
            elif self._conflict_strategy == ConflictStrategy.REMOTE_WINS:
                should_apply = state.version > self._local_state.version
            elif self._conflict_strategy == ConflictStrategy.LOCAL_WINS:
                should_apply = False
            elif self._conflict_strategy == ConflictStrategy.LATEST_WINS:
                should_apply = state.updated_at > self._local_state.updated_at

            if should_apply:
                self._local_state = state
                self._remote_version = state.version
                self._history.append(SyncEvent(
                    direction="pull", version=state.version, success=True,
                ))
                return True

            self._history.append(SyncEvent(
                direction="pull", version=state.version, success=False,
                error="Conflict: local state preferred",
            ))
            return False

    def get_pending_changes(self) -> list[dict[str, Any]]:
        with self._lock:
            return self._pending_changes.copy()

    def confirm_sync(self, up_to_version: int) -> int:
        """Confirm changes synced up to a version. Returns removed count."""
        with self._lock:
            before = len(self._pending_changes)
            self._pending_changes = [
                c for c in self._pending_changes if c["version"] > up_to_version
            ]
            removed = before - len(self._pending_changes)
            self._remote_version = max(self._remote_version, up_to_version)
            self._history.append(SyncEvent(
                direction="push", version=up_to_version, success=True,
            ))
            return removed

    def sync_history(self, limit: int = 20) -> list[SyncEvent]:
        return self._history[-limit:]

    def summary(self) -> dict[str, Any]:
        """summary ."""
        return {
            "local_version": self.local_version,
            "remote_version": self._remote_version,
            "pending_changes": self.pending_count,
            "is_synced": self.is_synced,
            "sync_events": len(self._history),
            "conflict_strategy": self._conflict_strategy.value,
        }
