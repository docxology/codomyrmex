"""UOR Graph — Content-addressed relationship graph.

Wraps EntityManager to add relationship management and BFS
path-finding, following the SocialGraph pattern from
codomyrmex.relations.network_analysis.
"""

from __future__ import annotations

from collections import deque
from typing import Any

from .entities import UOREntity, UORRelationship
from .manager import EntityManager


class UORGraph:
    """Content-addressed graph of UOR entities and relationships.

    Wraps an EntityManager (composition, not inheritance) and adds
    relationship storage, neighbor discovery, and BFS path-finding.

    Args:
        quantum: Quantum level for the underlying PrismEngine (default 0).
    """

    def __init__(self, quantum: int = 0) -> None:
        self._manager = EntityManager(quantum=quantum)
        self._relationships: dict[str, UORRelationship] = {}

    @property
    def manager(self) -> EntityManager:
        """The underlying EntityManager."""
        return self._manager

    # ═══════════════════════════════════════════════════════════════════════
    # ENTITY DELEGATION
    # ═══════════════════════════════════════════════════════════════════════

    def add_entity(
        self,
        name: str,
        entity_type: str = "generic",
        attributes: dict[str, Any] | None = None,
        compute_coordinates: bool = True,
    ) -> UOREntity:
        """Create and store a new entity. Delegates to EntityManager."""
        return self._manager.add_entity(
            name, entity_type, attributes, compute_coordinates
        )

    def get_entity(self, entity_id: str) -> UOREntity | None:
        """Retrieve an entity by ID."""
        return self._manager.get_entity(entity_id)

    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity and all its relationships.

        Returns:
            True if the entity was found and removed.
        """
        if not self._manager.remove_entity(entity_id):
            return False
        # Cascade: remove relationships involving this entity
        to_remove = [
            rid
            for rid, rel in self._relationships.items()
            if rel.source_id == entity_id or rel.target_id == entity_id
        ]
        for rid in to_remove:
            del self._relationships[rid]
        return True

    # ═══════════════════════════════════════════════════════════════════════
    # RELATIONSHIP MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str = "related",
        attributes: dict[str, Any] | None = None,
    ) -> UORRelationship | None:
        """Create a relationship between two entities.

        Both entities must already exist in the graph.

        Args:
            source_id: Source entity ID.
            target_id: Target entity ID.
            relationship_type: Category of relationship.
            attributes: Optional metadata.

        Returns:
            The created relationship, or None if either entity is missing.
        """
        if self._manager.get_entity(source_id) is None:
            return None
        if self._manager.get_entity(target_id) is None:
            return None

        attrs = attributes or {}
        rel = UORRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            attributes=attrs,
        )
        self._relationships[rel.id] = rel
        return rel

    def get_relationship(self, relationship_id: str) -> UORRelationship | None:
        """Retrieve a relationship by ID."""
        return self._relationships.get(relationship_id)

    def get_relationships(
        self,
        entity_id: str,
        relationship_type: str | None = None,
    ) -> list[UORRelationship]:
        """Get all relationships involving an entity.

        Args:
            entity_id: The entity to query.
            relationship_type: Optional filter by type.

        Returns:
            List of relationships where entity is source or target.
        """
        results: list[UORRelationship] = []
        for rel in self._relationships.values():
            if rel.source_id != entity_id and rel.target_id != entity_id:
                continue
            if relationship_type and rel.relationship_type != relationship_type:
                continue
            results.append(rel)
        return results

    def remove_relationship(self, relationship_id: str) -> bool:
        """Remove a relationship by ID.

        Returns:
            True if removed.
        """
        if relationship_id in self._relationships:
            del self._relationships[relationship_id]
            return True
        return False

    # ═══════════════════════════════════════════════════════════════════════
    # GRAPH TRAVERSAL
    # ═══════════════════════════════════════════════════════════════════════

    def get_neighbors(self, entity_id: str) -> list[UOREntity]:
        """Get entities directly connected to the given entity.

        Follows relationships in both directions (undirected semantics).

        Returns:
            List of neighbor entities (deduplicated).
        """
        neighbor_ids: set[str] = set()
        for rel in self._relationships.values():
            if rel.source_id == entity_id:
                neighbor_ids.add(rel.target_id)
            elif rel.target_id == entity_id:
                neighbor_ids.add(rel.source_id)

        neighbors: list[UOREntity] = []
        for nid in neighbor_ids:
            entity = self._manager.get_entity(nid)
            if entity is not None:
                neighbors.append(entity)
        return neighbors

    def find_path(self, source_id: str, target_id: str) -> list[str]:
        """Find shortest path between two entities via BFS.

        Args:
            source_id: Starting entity ID.
            target_id: Destination entity ID.

        Returns:
            Ordered list of entity IDs from source to target (inclusive).
            Empty list if no path exists or entities are missing.
        """
        if self._manager.get_entity(source_id) is None:
            return []
        if self._manager.get_entity(target_id) is None:
            return []
        if source_id == target_id:
            return [source_id]

        # Build adjacency index
        adjacency: dict[str, set[str]] = {}
        for rel in self._relationships.values():
            adjacency.setdefault(rel.source_id, set()).add(rel.target_id)
            adjacency.setdefault(rel.target_id, set()).add(rel.source_id)

        # BFS
        visited: set[str] = {source_id}
        queue: deque[list[str]] = deque([[source_id]])

        while queue:
            path = queue.popleft()
            current = path[-1]

            for neighbor in adjacency.get(current, set()):
                if neighbor == target_id:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return []

    # ═══════════════════════════════════════════════════════════════════════
    # PROPERTIES
    # ═══════════════════════════════════════════════════════════════════════

    @property
    def entity_count(self) -> int:
        """Number of entities in the graph."""
        return len(self._manager)

    @property
    def relationship_count(self) -> int:
        """Number of relationships in the graph."""
        return len(self._relationships)

    @property
    def all_relationships(self) -> list[UORRelationship]:
        """Read-only list of all relationships."""
        return list(self._relationships.values())

    def __len__(self) -> int:
        """Number of entities in the graph."""
        return self.entity_count

    def to_dict(self) -> dict[str, Any]:
        """Serialize the graph to a plain dictionary."""
        return {
            "entity_count": self.entity_count,
            "relationship_count": self.relationship_count,
            "entities": [
                e.to_dict() for e in self._manager.all_entities
            ],
            "relationships": [
                r.to_dict() for r in self._relationships.values()
            ],
        }

    def __repr__(self) -> str:
        """repr ."""
        return (
            f"UORGraph(entities={self.entity_count}, "
            f"relationships={self.relationship_count})"
        )
