"""Dead letter queue for failed event processing.

Captures events that fail processing, storing them with error context
for later inspection, retry, or manual resolution.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class DeadLetter:
    """An event that failed processing."""
    event_type: str
    payload: dict[str, Any]
    error: str
    error_type: str
    attempt_count: int = 1
    first_failure: float = field(default_factory=time.time)
    last_failure: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "event_type": self.event_type,
            "payload": self.payload,
            "error": self.error,
            "error_type": self.error_type,
            "attempt_count": self.attempt_count,
            "first_failure": self.first_failure,
            "last_failure": self.last_failure,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeadLetter:
        """Execute From Dict operations natively."""
        return cls(**data)


class DeadLetterQueue:
    """Persistent dead letter queue backed by JSONL file.

    Events that fail processing are stored here with error context.
    Supports inspection, retry, and purging.
    """

    def __init__(self, store_path: Path) -> None:
        """Execute   Init   operations natively."""
        self._path = store_path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def enqueue(self, event_type: str, payload: dict[str, Any],
                error: Exception, metadata: dict[str, Any] | None = None) -> DeadLetter:
        """Add a failed event to the dead letter queue."""
        letter = DeadLetter(
            event_type=event_type,
            payload=payload,
            error=str(error),
            error_type=type(error).__name__,
            metadata=metadata or {},
        )
        with open(self._path, "a") as f:
            f.write(json.dumps(letter.to_dict()) + "\n")
        return letter

    def list_all(self) -> list[DeadLetter]:
        """List all dead letters."""
        if not self._path.exists():
            return []
        letters = []
        with open(self._path) as f:
            for line in f:
                if line.strip():
                    letters.append(DeadLetter.from_dict(json.loads(line)))
        return letters

    def retry_all(self, handler: Callable[[str, dict[str, Any]], None]) -> tuple[int, int]:
        """Retry all dead letters. Returns (succeeded, failed)."""
        letters = self.list_all()
        succeeded, failed = 0, 0
        remaining: list[DeadLetter] = []
        for letter in letters:
            try:
                handler(letter.event_type, letter.payload)
                succeeded += 1
            except Exception as e:
                letter.attempt_count += 1
                letter.last_failure = time.time()
                letter.error = str(e)
                letter.error_type = type(e).__name__
                remaining.append(letter)
                failed += 1
        # Rewrite with only remaining failures
        with open(self._path, "w") as f:
            for letter in remaining:
                f.write(json.dumps(letter.to_dict()) + "\n")
        return succeeded, failed

    def purge(self) -> int:
        """Remove all dead letters. Returns count purged."""
        count = len(self.list_all())
        if self._path.exists():
            self._path.write_text("")
        return count

    @property
    def count(self) -> int:
        """Execute Count operations natively."""
        return len(self.list_all())
