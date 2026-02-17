"""Derivation Tracking — Provenance certificates for UOR operations.

Records the provenance of entity and relationship changes as
content-addressed derivation certificates, following the PRISM
derivation model.

References:
    - https://github.com/UOR-Foundation/prism (Derivation class)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class DerivationRecord:
    """An immutable provenance certificate for a UOR operation.

    The derivation ID is content-addressed: identical inputs and
    operations always produce the same ID.

    Attributes:
        id: Content-addressed ID (SHA256 of operation + inputs + result).
        entity_id: The entity this derivation pertains to.
        operation: The operation performed (e.g., 'create', 'update', 'relate').
        inputs: Dictionary of input data for the operation.
        result_hash: Content hash of the resulting state.
        timestamp: ISO-format timestamp when the derivation was created.
    """

    entity_id: str
    operation: str
    inputs: dict[str, Any] = field(default_factory=dict)
    result_hash: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    id: str = field(default="")

    def __post_init__(self) -> None:
        if not self.id:
            object.__setattr__(
                self, "id", self._compute_derivation_id(
                    self.entity_id, self.operation, self.inputs, self.result_hash
                )
            )

    @staticmethod
    def _compute_derivation_id(
        entity_id: str,
        operation: str,
        inputs: dict[str, Any],
        result_hash: str,
    ) -> str:
        """Compute the content-addressed derivation URN."""
        content = json.dumps(
            {
                "entity_id": entity_id,
                "operation": operation,
                "inputs": inputs,
                "result_hash": result_hash,
            },
            sort_keys=True,
            default=str,
        )
        hex_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
        return f"urn:uor:derivation:sha256:{hex_digest}"


class DerivationTracker:
    """Append-only log of derivation records for provenance tracking.

    Provides recording, retrieval, and chain verification.
    """

    def __init__(self) -> None:
        self._records: list[DerivationRecord] = []

    def record(
        self,
        entity_id: str,
        operation: str,
        inputs: dict[str, Any] | None = None,
        result_hash: str = "",
    ) -> DerivationRecord:
        """Create and store a new derivation record.

        Args:
            entity_id: The entity this operation pertains to.
            operation: Operation name (e.g., 'create', 'update', 'delete').
            inputs: Input data for the operation.
            result_hash: Content hash of the resulting entity state.

        Returns:
            The created DerivationRecord.
        """
        record = DerivationRecord(
            entity_id=entity_id,
            operation=operation,
            inputs=inputs or {},
            result_hash=result_hash,
        )
        self._records.append(record)
        return record

    def get_history(self, entity_id: str) -> list[DerivationRecord]:
        """Retrieve the derivation history for an entity.

        Args:
            entity_id: The entity to query.

        Returns:
            List of derivation records in chronological order.
        """
        return [r for r in self._records if r.entity_id == entity_id]

    def verify_chain(self, entity_id: str) -> bool:
        """Verify that derivation IDs are consistent for an entity.

        Recomputes each derivation ID and checks it matches the stored ID.
        This ensures no records have been tampered with.

        Args:
            entity_id: The entity to verify.

        Returns:
            True if all derivation IDs are consistent.

        Raises:
            RuntimeError: If a derivation ID mismatch is detected.
        """
        history = self.get_history(entity_id)
        for record in history:
            expected_id = DerivationRecord._compute_derivation_id(
                record.entity_id, record.operation,
                record.inputs, record.result_hash,
            )
            if record.id != expected_id:
                raise RuntimeError(
                    f"Derivation chain broken for entity {entity_id}: "
                    f"expected {expected_id}, got {record.id}"
                )
        return True

    @property
    def all_records(self) -> list[DerivationRecord]:
        """Read-only list of all derivation records."""
        return list(self._records)

    def __len__(self) -> int:
        return len(self._records)
