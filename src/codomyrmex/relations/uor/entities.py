"""UOR Entities — Content-addressed entities with triadic coordinates.

Provides UOREntity and UORRelationship dataclasses that combine
content-addressed hashing (SHA256) with PRISM triadic coordinates
for structural identity.

References:
    - https://github.com/UOR-Foundation/UOR-Framework
    - https://github.com/UOR-Foundation/prism
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .engine import TriadicCoordinate


def _content_hash(data: dict[str, Any]) -> str:
    """Compute SHA256 content hash of a dictionary.

    Uses sorted keys for deterministic serialization, matching
    the pattern in codomyrmex.utils.hashing.dict_hash.
    """
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass
class UOREntity:
    """A content-addressed entity with optional triadic coordinates.

    Identity is derived from the entity's intrinsic attributes (name,
    entity_type, attributes) rather than from external storage location.

    Attributes:
        id: Unique identifier (UUID4).
        name: Human-readable entity name.
        entity_type: Category or type classification.
        attributes: Arbitrary key-value metadata.
        content_hash: SHA256 hash of (name, entity_type, attributes).
        triadic_coordinates: PRISM coordinates if computed.
        created_at: ISO-format creation timestamp.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    entity_type: str = "generic"
    attributes: dict[str, Any] = field(default_factory=dict)
    content_hash: str = ""
    triadic_coordinates: TriadicCoordinate | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        """Compute content hash from intrinsic attributes if not set."""
        if not self.content_hash:
            self.content_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute content hash from name, type, and attributes."""
        return _content_hash({
            "name": self.name,
            "entity_type": self.entity_type,
            "attributes": self.attributes,
        })

    def recompute_hash(self) -> str:
        """Recompute and update the content hash after attribute changes.

        Returns:
            The new content hash.
        """
        self.content_hash = self._compute_hash()
        return self.content_hash

    def to_dict(self) -> dict[str, Any]:
        """Serialize the entity to a plain dictionary."""
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type,
            "attributes": self.attributes,
            "content_hash": self.content_hash,
            "created_at": self.created_at,
        }
        if self.triadic_coordinates is not None:
            result["triadic_coordinates"] = {
                "datum": list(self.triadic_coordinates.datum),
                "stratum": list(self.triadic_coordinates.stratum),
                "spectrum": [list(s) for s in self.triadic_coordinates.spectrum],
                "total_stratum": self.triadic_coordinates.total_stratum,
            }
        return result


@dataclass
class UORRelationship:
    """A content-addressed relationship between two UOR entities.

    The relationship hash is derived from the source, target, type,
    and attributes — ensuring identical relationships always produce
    the same hash regardless of when or where they are created.

    Attributes:
        id: Unique identifier (UUID4).
        source_id: ID of the source entity.
        target_id: ID of the target entity.
        relationship_type: Category of the relationship.
        attributes: Arbitrary key-value metadata.
        relationship_hash: SHA256 hash of (source_id, target_id, type, attributes).
        created_at: ISO-format creation timestamp.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    source_id: str = ""
    target_id: str = ""
    relationship_type: str = "related"
    attributes: dict[str, Any] = field(default_factory=dict)
    relationship_hash: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        """Compute relationship hash if not set."""
        if not self.relationship_hash:
            self.relationship_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute content hash from relationship attributes."""
        return _content_hash({
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "attributes": self.attributes,
        })

    def to_dict(self) -> dict[str, Any]:
        """Serialize the relationship to a plain dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "attributes": self.attributes,
            "relationship_hash": self.relationship_hash,
            "created_at": self.created_at,
        }
