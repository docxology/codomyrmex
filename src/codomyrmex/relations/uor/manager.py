"""Entity Manager — CRUD and similarity search for UOR entities.

Follows the ContactManager pattern from codomyrmex.relations.crm
with private dict storage, search, and PRISM-based similarity.
"""

from __future__ import annotations

from typing import Any

from .engine import PrismEngine, TriadicCoordinate
from .entities import UOREntity


class EntityManager:
    """Manages a collection of UOR entities with search and similarity.

    Provides CRUD operations, text search, PRISM-based similarity
    search via triadic coordinate fidelity, and duplicate detection
    via content hashing.

    Args:
        quantum: Quantum level for the PRISM engine (default 0 = 8-bit).
    """

    def __init__(self, quantum: int = 0) -> None:
        """Initialize this instance."""
        self._entities: dict[str, UOREntity] = {}
        self._engine = PrismEngine(quantum=quantum)

    @property
    def engine(self) -> PrismEngine:
        """The underlying PrismEngine instance."""
        return self._engine

    def add_entity(
        self,
        name: str,
        entity_type: str = "generic",
        attributes: dict[str, Any] | None = None,
        compute_coordinates: bool = True,
    ) -> UOREntity:
        """Create and store a new UOR entity.

        Args:
            name: Human-readable entity name.
            entity_type: Category classification.
            attributes: Optional key-value metadata.
            compute_coordinates: If True, compute triadic coordinates
                from the content hash.

        Returns:
            The newly created UOREntity.
        """
        attrs = attributes or {}
        entity = UOREntity(name=name, entity_type=entity_type, attributes=attrs)

        if compute_coordinates:
            entity.triadic_coordinates = self._compute_coordinates(entity)

        self._entities[entity.id] = entity
        return entity

    def get_entity(self, entity_id: str) -> UOREntity | None:
        """Retrieve an entity by ID.

        Returns:
            The entity if found, otherwise None.
        """
        return self._entities.get(entity_id)

    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity by ID.

        Returns:
            True if the entity was found and removed.
        """
        if entity_id in self._entities:
            del self._entities[entity_id]
            return True
        return False

    def search_entities(
        self,
        query: str,
        entity_type: str | None = None,
    ) -> list[UOREntity]:
        """Search entities by name, type, or attribute values.

        Case-insensitive substring matching against name, entity_type,
        and string values in attributes.

        Args:
            query: Search string.
            entity_type: Optional type filter (exact match).

        Returns:
            List of matching entities.
        """
        q = query.lower()
        results: list[UOREntity] = []
        for entity in self._entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue
            matched = (
                q in entity.name.lower()
                or q in entity.entity_type.lower()
                or any(q in str(v).lower() for v in entity.attributes.values())
            )
            if matched:
                results.append(entity)
        return results

    def find_similar(
        self,
        entity_id: str,
        threshold: float = 0.5,
    ) -> list[tuple[UOREntity, float]]:
        """Find entities similar to a reference entity by triadic fidelity.

        Uses PRISM Hamming-distance fidelity to compare content hashes
        projected into coordinate space.

        Args:
            entity_id: Reference entity ID.
            threshold: Minimum fidelity score (0.0 to 1.0).

        Returns:
            List of (entity, fidelity) tuples, sorted by descending fidelity.
            Excludes the reference entity itself.
        """
        ref = self._entities.get(entity_id)
        if ref is None:
            return []

        if ref.triadic_coordinates is None:
            return []

        ref_value = self._hash_to_int(ref.content_hash)
        results: list[tuple[UOREntity, float]] = []

        for entity in self._entities.values():
            if entity.id == entity_id:
                continue
            if entity.triadic_coordinates is None:
                continue

            entity_value = self._hash_to_int(entity.content_hash)
            fid = self._engine.fidelity(ref_value, entity_value)

            if fid >= threshold:
                results.append((entity, fid))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def find_duplicates(self) -> list[list[UOREntity]]:
        """Find groups of entities with identical content hashes.

        Returns:
            List of groups, where each group contains 2+ entities
            sharing the same content hash.
        """
        hash_groups: dict[str, list[UOREntity]] = {}
        for entity in self._entities.values():
            hash_groups.setdefault(entity.content_hash, []).append(entity)
        return [group for group in hash_groups.values() if len(group) > 1]

    @property
    def all_entities(self) -> list[UOREntity]:
        """Read-only list of all entities."""
        return list(self._entities.values())

    def __len__(self) -> int:
        """len ."""
        return len(self._entities)

    def __repr__(self) -> str:
        """repr ."""
        return f"EntityManager(entities={len(self)}, quantum={self._engine.quantum})"

    def _compute_coordinates(self, entity: UOREntity) -> TriadicCoordinate:
        """Compute triadic coordinates from entity content hash."""
        value = self._hash_to_int(entity.content_hash)
        return self._engine.triad(value)

    def _hash_to_int(self, hex_hash: str) -> int:
        """Convert hex hash to integer, reduced to engine width."""
        # Use first `width` bytes of the hash
        full_int = int(hex_hash[: self._engine.width * 2], 16)
        return full_int & self._engine._mask
