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
from datetime import UTC, datetime
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
        default_factory=lambda: datetime.now(UTC).isoformat()
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

    def has_attribute(self, key: str) -> bool:
        """Check if the entity has a specific attribute."""
        return key in self.attributes

    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute and recompute the content hash."""
        self.attributes[key] = value
        self.recompute_hash()

    def remove_attribute(self, key: str) -> Any | None:
        """Remove an attribute and recompute the hash. Returns the removed value."""
        value = self.attributes.pop(key, None)
        if value is not None:
            self.recompute_hash()
        return value

    def merge_attributes(self, other: UOREntity, overwrite: bool = False) -> None:
        """Merge attributes from another entity.

        Args:
            other: Source entity to merge from.
            overwrite: If True, overwrite existing keys.
        """
        for k, v in other.attributes.items():
            if overwrite or k not in self.attributes:
                self.attributes[k] = v
        self.recompute_hash()

    def similarity_score(self, other: UOREntity) -> float:
        """Compute a simple attribute overlap score between [0, 1]."""
        if not self.attributes and not other.attributes:
            return 1.0 if self.entity_type == other.entity_type else 0.0
        all_keys = set(self.attributes) | set(other.attributes)
        if not all_keys:
            return 0.0
        matching = sum(
            1 for k in all_keys
            if self.attributes.get(k) == other.attributes.get(k)
        )
        return matching / len(all_keys)


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
        weight: Numeric strength of the relationship (default 1.0).
        bidirectional: Whether the relationship is undirected.
        created_at: ISO-format creation timestamp.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    source_id: str = ""
    target_id: str = ""
    relationship_type: str = "related"
    attributes: dict[str, Any] = field(default_factory=dict)
    relationship_hash: str = ""
    weight: float = 1.0
    bidirectional: bool = False
    created_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
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

    def inverse(self) -> UORRelationship:
        """Create the inverse relationship (swap source and target)."""
        return UORRelationship(
            source_id=self.target_id,
            target_id=self.source_id,
            relationship_type=f"inverse_{self.relationship_type}",
            attributes=self.attributes,
            weight=self.weight,
            bidirectional=self.bidirectional,
        )

    def involves(self, entity_id: str) -> bool:
        """Check if an entity is involved in this relationship."""
        return self.source_id == entity_id or self.target_id == entity_id

    def to_dict(self) -> dict[str, Any]:
        """Serialize the relationship to a plain dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "attributes": self.attributes,
            "relationship_hash": self.relationship_hash,
            "weight": self.weight,
            "bidirectional": self.bidirectional,
            "created_at": self.created_at,
        }

