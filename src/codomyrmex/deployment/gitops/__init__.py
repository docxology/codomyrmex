"""
GitOps integration for deployment synchronization.

Provides a GitOpsSynchronizer that detects drift between a Git repository's
desired state and the actual deployed state, and can reconcile differences.
"""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class SyncState(Enum):
    """Synchronisation states between desired and actual."""
    IN_SYNC = "in_sync"
    DRIFTED = "drifted"
    UNKNOWN = "unknown"
    SYNCING = "syncing"
    ERROR = "error"


@dataclass
class SyncStatus:
    """Snapshot of the current synchronization state.

    Attributes:
        state: The current sync state.
        desired_revision: The Git revision that represents the desired state.
        actual_revision: The Git revision that is currently deployed.
        last_synced_at: When the last successful sync occurred.
        drift_details: Description of detected differences, if any.
    """
    state: SyncState
    desired_revision: str | None = None
    actual_revision: str | None = None
    last_synced_at: datetime | None = None
    drift_details: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "state": self.state.value,
            "desired_revision": self.desired_revision,
            "actual_revision": self.actual_revision,
            "last_synced_at": (
                self.last_synced_at.isoformat() if self.last_synced_at else None
            ),
            "drift_details": self.drift_details,
        }


class GitOpsSynchronizer:
    """Synchronizes deployed state with a Git repository.

    The synchronizer tracks a *desired* revision (from a Git repository)
    and an *actual* revision (what is currently deployed).  It can detect
    drift and trigger reconciliation.

    Args:
        repo_path: Local filesystem path to the Git repository.
        target_branch: The branch representing the desired state
                       (default ``"main"``).
    """

    def __init__(
        self,
        repo_path: str,
        target_branch: str = "main",
    ) -> None:
        self._repo_path = repo_path
        self._target_branch = target_branch
        self._actual_revision: str | None = None
        self._last_synced_at: datetime | None = None
        self._drift_details: list[str] = []
        self._state = SyncState.UNKNOWN

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sync_state(self) -> SyncStatus:
        """Fetch the latest desired revision and compare with actual.

        Runs ``git rev-parse`` on the target branch to determine the
        desired revision, then compares with the tracked actual revision.

        Returns:
            A SyncStatus reflecting the comparison.
        """
        desired = self._get_head_revision()
        if desired is None:
            self._state = SyncState.ERROR
            return self._build_status(desired)

        if self._actual_revision is None:
            self._state = SyncState.UNKNOWN
        elif desired == self._actual_revision:
            self._state = SyncState.IN_SYNC
            self._drift_details = []
        else:
            self._state = SyncState.DRIFTED
            self._drift_details = [
                f"desired={desired[:12]}, actual={self._actual_revision[:12]}"
            ]

        return self._build_status(desired)

    def detect_drift(self) -> bool:
        """Return True if the desired and actual revisions differ.

        This is a convenience wrapper around :meth:`sync_state`.

        Returns:
            True if drift is detected, False if in sync or state is unknown.
        """
        status = self.sync_state()
        return status.state == SyncState.DRIFTED

    def reconcile(self) -> SyncStatus:
        """Reconcile drift by updating the actual revision to match desired.

        In a real deployment this would trigger the deployment pipeline.
        Here it updates the internal tracking state.

        Returns:
            The SyncStatus after reconciliation.
        """
        desired = self._get_head_revision()
        if desired is None:
            self._state = SyncState.ERROR
            return self._build_status(desired)

        self._state = SyncState.SYNCING
        # In a production system this is where the deploy would happen.
        self._actual_revision = desired
        self._last_synced_at = datetime.now()
        self._state = SyncState.IN_SYNC
        self._drift_details = []

        return self._build_status(desired)

    def get_sync_status(self) -> SyncStatus:
        """Return the last known sync status without re-fetching.

        Returns:
            A SyncStatus based on the most recent internal state.
        """
        desired = self._get_head_revision()
        return self._build_status(desired)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_head_revision(self) -> str | None:
        """Resolve the HEAD of the target branch via ``git rev-parse``."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", self._target_branch],
                cwd=self._repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning("Failed to resolve HEAD revision for branch %s: %s", self._target_branch, e)
            return None

    def _build_status(self, desired: str | None) -> SyncStatus:
        return SyncStatus(
            state=self._state,
            desired_revision=desired,
            actual_revision=self._actual_revision,
            last_synced_at=self._last_synced_at,
            drift_details=list(self._drift_details),
        )

    def __repr__(self) -> str:
        """repr ."""
        return (
            f"GitOpsSynchronizer(repo={self._repo_path!r}, "
            f"branch={self._target_branch!r}, state={self._state.value})"
        )


__all__ = [
    "GitOpsSynchronizer",
    "SyncState",
    "SyncStatus",
]
