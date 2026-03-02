"""Durable agent state checkpointing.

Saves and loads agent snapshots to/from disk as JSON files
with metadata for diff-based state comparison.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from codomyrmex.agents.transport.serializer import AgentSerializer, AgentSnapshot


@dataclass
class StateDelta:
    """Differences between two checkpoints.

    Attributes:
        config_changed: Whether config differs.
        traces_added: Number of new traces.
        memory_keys_added: New memory keys.
        memory_keys_removed: Removed memory keys.
        memory_keys_modified: Modified memory keys.
    """

    config_changed: bool = False
    traces_added: int = 0
    memory_keys_added: list[str] = field(default_factory=list)
    memory_keys_removed: list[str] = field(default_factory=list)
    memory_keys_modified: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return (
            self.config_changed
            or self.traces_added > 0
            or bool(self.memory_keys_added)
            or bool(self.memory_keys_removed)
            or bool(self.memory_keys_modified)
        )


@dataclass
class Checkpoint:
    """Durable agent state checkpoint.

    Wraps an AgentSnapshot with persistence and diff capabilities.

    Attributes:
        snapshot: The agent state snapshot.
        checkpoint_id: Unique checkpoint identifier.
        created_at: Checkpoint creation timestamp.
    """

    snapshot: AgentSnapshot
    checkpoint_id: str = ""
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.checkpoint_id:
            self.checkpoint_id = (
                f"ckpt-{self.snapshot.agent_id}-{int(self.created_at)}"
            )

    def save(self, path: str | Path) -> None:
        """Save checkpoint to a JSON file.

        Args:
            path: File path to save to.
        """
        serializer = AgentSerializer()
        data = json.loads(serializer.serialize(self.snapshot))
        checkpoint_data = {
            "checkpoint_id": self.checkpoint_id,
            "created_at": self.created_at,
            "snapshot": data,
        }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(checkpoint_data, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> Checkpoint:
        """Load a checkpoint from a JSON file.

        Args:
            path: File path to load from.

        Returns:
            Restored Checkpoint.
        """
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        snap_data = raw["snapshot"]
        snapshot = AgentSnapshot(
            agent_id=snap_data["agent_id"],
            agent_type=snap_data.get("agent_type", ""),
            config=snap_data.get("config", {}),
            traces=snap_data.get("traces", []),
            memory=snap_data.get("memory", {}),
            metadata=snap_data.get("metadata", {}),
            timestamp=snap_data.get("timestamp", 0.0),
            version=snap_data.get("version", "1.0"),
        )
        return cls(
            snapshot=snapshot,
            checkpoint_id=raw["checkpoint_id"],
            created_at=raw["created_at"],
        )

    def diff(self, other: Checkpoint) -> StateDelta:
        """Compute differences between this and another checkpoint.

        Args:
            other: The checkpoint to compare against.

        Returns:
            StateDelta describing the differences.
        """
        delta = StateDelta()

        # Config diff
        delta.config_changed = self.snapshot.config != other.snapshot.config

        # Traces diff
        delta.traces_added = max(
            0, len(other.snapshot.traces) - len(self.snapshot.traces),
        )

        # Memory diff
        self_keys = set(self.snapshot.memory.keys())
        other_keys = set(other.snapshot.memory.keys())
        delta.memory_keys_added = sorted(other_keys - self_keys)
        delta.memory_keys_removed = sorted(self_keys - other_keys)
        delta.memory_keys_modified = sorted(
            k for k in self_keys & other_keys
            if self.snapshot.memory[k] != other.snapshot.memory[k]
        )

        return delta


__all__ = ["Checkpoint", "StateDelta"]
