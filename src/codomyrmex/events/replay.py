"""Event replay and sourcing for debugging and recovery.

Provides event store, replay mechanisms, and event sourcing patterns
to reconstruct state from event history.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class StoredEvent:
    """An event persisted in the event store."""
    event_type: str
    payload: dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    sequence_number: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "sequence_number": self.sequence_number,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StoredEvent:
        return cls(**data)


class EventStore:
    """Append-only event store with replay capabilities.

    Stores events to a JSONL file and supports replaying them
    in sequence order for state reconstruction.
    """

    def __init__(self, store_path: Path) -> None:
        self._path = store_path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._sequence = self._load_last_sequence()

    def _load_last_sequence(self) -> int:
        if not self._path.exists():
            return 0
        last_seq = 0
        with open(self._path) as f:
            for line in f:
                if line.strip():
                    evt = json.loads(line)
                    last_seq = max(last_seq, evt.get("sequence_number", 0))
        return last_seq

    def append(self, event_type: str, payload: dict[str, Any],
               metadata: dict[str, Any] | None = None) -> StoredEvent:
        """Append a new event to the store."""
        self._sequence += 1
        event = StoredEvent(
            event_type=event_type,
            payload=payload,
            sequence_number=self._sequence,
            metadata=metadata or {},
        )
        with open(self._path, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")
        return event

    def replay(
        self,
        handler: Callable[[StoredEvent], None],
        *,
        from_sequence: int = 0,
        event_types: set[str] | None = None,
    ) -> int:
        """Replay events through a handler function.

        Args:
            handler: Function called for each replayed event.
            from_sequence: Start replaying from this sequence number.
            event_types: Only replay these event types (None = all).

        Returns:
            Number of events replayed.
        """
        count = 0
        if not self._path.exists():
            return count
        with open(self._path) as f:
            for line in f:
                if not line.strip():
                    continue
                event = StoredEvent.from_dict(json.loads(line))
                if event.sequence_number < from_sequence:
                    continue
                if event_types and event.event_type not in event_types:
                    continue
                handler(event)
                count += 1
        return count

    def snapshot(self, state: dict[str, Any], snapshot_path: Path) -> None:
        """Save a state snapshot for faster recovery."""
        data = {
            "state": state,
            "last_sequence": self._sequence,
            "timestamp": time.time(),
        }
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        with open(snapshot_path, "w") as f:
            json.dump(data, f, indent=2)

    def load_snapshot(self, snapshot_path: Path) -> tuple[dict[str, Any], int]:
        """Load a state snapshot. Returns (state, last_sequence)."""
        with open(snapshot_path) as f:
            data = json.load(f)
        return data["state"], data["last_sequence"]

    @property
    def event_count(self) -> int:
        return self._sequence
