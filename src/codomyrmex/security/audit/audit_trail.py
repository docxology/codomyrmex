"""Immutable, signed audit trail for agent actions.

Records all agent actions with HMAC-SHA256 chain integrity.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class AuditEntry:
    """A single audit trail entry.

    Attributes:
        action: Action performed.
        actor: Who performed it.
        resource: What was affected.
        timestamp: When it occurred.
        metadata: Additional details.
        previous_hash: Hash of previous entry (chain).
        entry_hash: This entry's hash.
    """

    action: str
    actor: str = ""
    resource: str = ""
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    previous_hash: str = ""
    entry_hash: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "action": self.action,
            "actor": self.actor,
            "resource": self.resource,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
        }

    def payload(self) -> str:
        """Payload."""
        return json.dumps({
            "action": self.action,
            "actor": self.actor,
            "resource": self.resource,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
        }, sort_keys=True)


class AuditTrail:
    """Append-only, HMAC-chained audit trail.

    Usage::

        trail = AuditTrail(signing_key=b"secret")
        trail.record("deploy", actor="agent-1", resource="prod")
        assert trail.verify_chain()
    """

    def __init__(self, signing_key: bytes = b"codomyrmex-audit") -> None:
        self._key = signing_key
        self._entries: list[AuditEntry] = []

    def record(
        self,
        action: str,
        actor: str = "",
        resource: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Append an audit entry with chain integrity."""
        prev_hash = self._entries[-1].entry_hash if self._entries else "genesis"
        entry = AuditEntry(
            action=action,
            actor=actor,
            resource=resource,
            metadata=metadata or {},
            previous_hash=prev_hash,
        )
        entry.entry_hash = self._compute_hash(entry)
        self._entries.append(entry)

        logger.info("Audit recorded", extra={"action": action, "actor": actor})
        return entry

    def verify_chain(self) -> bool:
        """Verify the integrity of the entire audit chain."""
        for i, entry in enumerate(self._entries):
            expected_prev = self._entries[i - 1].entry_hash if i > 0 else "genesis"
            if entry.previous_hash != expected_prev:
                return False
            if entry.entry_hash != self._compute_hash(entry):
                return False
        return True

    @property
    def size(self) -> int:
        """Size."""
        return len(self._entries)

    def entries(self) -> list[AuditEntry]:
        """Entries."""
        return list(self._entries)

    def entries_by_actor(self, actor: str) -> list[AuditEntry]:
        return [e for e in self._entries if e.actor == actor]

    def to_jsonl(self) -> str:
        return "\n".join(json.dumps(e.to_dict()) for e in self._entries)

    def _compute_hash(self, entry: AuditEntry) -> str:
        return hmac.new(self._key, entry.payload().encode(), hashlib.sha256).hexdigest()[:16]


__all__ = ["AuditEntry", "AuditTrail"]
