"""
Rollback management for deployments.

Provides a RollbackManager that creates deployment snapshots and allows
reverting to previous versions with verification.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SnapshotState(Enum):
    """Lifecycle states of a deployment snapshot."""
    ACTIVE = "active"
    ROLLED_BACK = "rolled_back"
    SUPERSEDED = "superseded"


@dataclass
class DeploymentSnapshot:
    """A point-in-time snapshot of a deployment.

    Attributes:
        version: The version string captured in this snapshot.
        state: Current lifecycle state of the snapshot.
        created_at: When the snapshot was taken.
        metadata: Arbitrary metadata about the deployment at snapshot time
                  (e.g. target count, config hash, environment variables).
    """
    version: str
    state: SnapshotState = SnapshotState.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialise the snapshot to a plain dictionary."""
        return {
            "version": self.version,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class RollbackResult:
    """Outcome of a rollback operation.

    Attributes:
        success: True if the rollback completed without errors.
        from_version: The version before the rollback.
        to_version: The version that was restored.
        performed_at: When the rollback was executed.
        message: A human-readable summary.
    """
    success: bool
    from_version: str
    to_version: str
    performed_at: datetime = field(default_factory=datetime.now)
    message: str = ""


class RollbackManager:
    """Manages deployment snapshots and rollback operations.

    Snapshots form a chronological stack.  Rolling back restores the most
    recent non-rolled-back snapshot (or a specific version) and marks
    intermediate snapshots as superseded.
    """

    def __init__(self) -> None:
        self._snapshots: list[DeploymentSnapshot] = []
        self._current_version: str | None = None

    def create_snapshot(
        self,
        version: str,
        metadata: dict[str, Any] | None = None,
    ) -> DeploymentSnapshot:
        """Create a new deployment snapshot.

        Any previously active snapshot is marked as superseded.

        Args:
            version: Version string of the deployment being snapshotted.
            metadata: Optional extra data to store in the snapshot.

        Returns:
            The newly created DeploymentSnapshot.
        """
        # Supersede the current active snapshot
        for snap in self._snapshots:
            if snap.state == SnapshotState.ACTIVE:
                snap.state = SnapshotState.SUPERSEDED

        snapshot = DeploymentSnapshot(
            version=version,
            metadata=metadata or {},
        )
        self._snapshots.append(snapshot)
        self._current_version = version
        return snapshot

    def rollback_to(self, version: str) -> RollbackResult:
        """Rollback the deployment to a previously snapshotted version.

        The matching snapshot is marked ROLLED_BACK (indicating it was the
        restore target) and all snapshots created after it are marked
        SUPERSEDED.

        Args:
            version: The target version to restore.

        Returns:
            A RollbackResult describing the outcome.

        Raises:
            KeyError: If no snapshot with the given version exists.
        """
        target_index: int | None = None
        for i, snap in enumerate(self._snapshots):
            if snap.version == version:
                target_index = i
                break

        if target_index is None:
            raise KeyError(f"No snapshot found for version: {version}")

        from_version = self._current_version or "unknown"

        # Mark later snapshots as superseded
        for snap in self._snapshots[target_index + 1:]:
            snap.state = SnapshotState.SUPERSEDED

        self._snapshots[target_index].state = SnapshotState.ROLLED_BACK
        self._current_version = version

        return RollbackResult(
            success=True,
            from_version=from_version,
            to_version=version,
            message=f"Rolled back from {from_version} to {version}",
        )

    def list_snapshots(self) -> list[DeploymentSnapshot]:
        """Return all snapshots in chronological order.

        Returns:
            A list of DeploymentSnapshot instances (copies).
        """
        return [copy.copy(s) for s in self._snapshots]

    def verify_rollback(self) -> bool:
        """Verify that the current deployment matches the rollback target.

        A rollback is considered verified if there is exactly one snapshot
        in the ROLLED_BACK state and its version matches the current
        tracked version.

        Returns:
            True if the rollback state is consistent.
        """
        rolled_back = [
            s for s in self._snapshots
            if s.state == SnapshotState.ROLLED_BACK
        ]
        if len(rolled_back) != 1:
            return False
        return rolled_back[0].version == self._current_version

    @property
    def current_version(self) -> str | None:
        """The version currently considered active."""
        return self._current_version

    def __repr__(self) -> str:
        return (
            f"RollbackManager(snapshots={len(self._snapshots)}, "
            f"current_version={self._current_version!r})"
        )


__all__ = [
    "DeploymentSnapshot",
    "RollbackManager",
    "RollbackResult",
    "SnapshotState",
]
