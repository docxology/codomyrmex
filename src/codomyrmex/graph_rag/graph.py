"""
Knowledge Graph

In-memory knowledge graph for entity and relationship storage.
"""

import threading

from .models import Entity, EntityType, Relationship


class KnowledgeGraph:
    """
    In-memory knowledge graph for entity and relationship storage.

    Usage:
        graph = KnowledgeGraph()

        # Add entities
        graph.add_entity(Entity(id="python", name="Python", entity_type=EntityType.CONCEPT))
        graph.add_entity(Entity(id="ai", name="Artificial Intelligence", entity_type=EntityType.CONCEPT))

        # Add relationship
        graph.add_relationship(Relationship(
            source_id="python",
            target_id="ai",
            relation_type=RelationType.RELATED_TO,
        ))

        # Query
        related = graph.get_neighbors("python")
    """

    def __init__(self):
        """Initialize this instance."""
        self._entities: dict[str, Entity] = {}
        self._relationships: list[Relationship] = []
        self._adjacency: dict[str, list[str]] = {}  # source_id -> [target_ids]
        self._reverse_adjacency: dict[str, list[str]] = {}  # target_id -> [source_ids]
        self._lock = threading.Lock()

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the graph."""
        with self._lock:
            self._entities[entity.id] = entity
            if entity.id not in self._adjacency:
                self._adjacency[entity.id] = []
            if entity.id not in self._reverse_adjacency:
                self._reverse_adjacency[entity.id] = []

    def get_entity(self, entity_id: str) -> Entity | None:
        """Get an entity by ID."""
        return self._entities.get(entity_id)

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the graph."""
        with self._lock:
            self._relationships.append(relationship)

            if relationship.source_id not in self._adjacency:
                self._adjacency[relationship.source_id] = []
            self._adjacency[relationship.source_id].append(relationship.target_id)

            if relationship.target_id not in self._reverse_adjacency:
                self._reverse_adjacency[relationship.target_id] = []
            self._reverse_adjacency[relationship.target_id].append(relationship.source_id)

    def get_neighbors(
        self,
        entity_id: str,
        direction: str = "both",
    ) -> list[Entity]:
        """Get neighboring entities."""
        neighbor_ids: set[str] = set()

        if direction in ["out", "both"]:
            neighbor_ids.update(self._adjacency.get(entity_id, []))

        if direction in ["in", "both"]:
            neighbor_ids.update(self._reverse_adjacency.get(entity_id, []))

        return [self._entities[nid] for nid in neighbor_ids if nid in self._entities]

    def get_relationships(
        self,
        entity_id: str,
        direction: str = "both",
    ) -> list[Relationship]:
        """Get relationships involving an entity."""
        results = []
        for r in self._relationships:
            if direction in ["out", "both"] and r.source_id == entity_id:
                results.append(r)
            if direction in ["in", "both"] and r.target_id == entity_id:
                results.append(r)
        return results

    def find_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 5,
    ) -> list[str] | None:
        """Find shortest path between two entities (BFS)."""
        if start_id == end_id:
            return [start_id]

        visited = {start_id}
        queue = [[start_id]]

        while queue:
            path = queue.pop(0)
            if len(path) > max_depth:
                break

            current = path[-1]
            for neighbor_id in self._adjacency.get(current, []):
                if neighbor_id == end_id:
                    return path + [neighbor_id]

                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append(path + [neighbor_id])

        return None

    def subgraph(
        self,
        entity_ids: list[str],
        include_neighbors: bool = True,
    ) -> "KnowledgeGraph":
        """Extract a subgraph containing specified entities."""
        subgraph = KnowledgeGraph()
        target_ids = set(entity_ids)

        # Add specified entities
        for eid in entity_ids:
            entity = self.get_entity(eid)
            if entity:
                subgraph.add_entity(entity)

                # Add neighbors if requested
                if include_neighbors:
                    for neighbor in self.get_neighbors(eid):
                        subgraph.add_entity(neighbor)
                        target_ids.add(neighbor.id)

        # Add relationships between included entities
        for r in self._relationships:
            if r.source_id in target_ids and r.target_id in target_ids:
                subgraph.add_relationship(r)

        return subgraph

    def search_entities(
        self,
        query: str,
        entity_type: EntityType | None = None,
        limit: int = 10,
    ) -> list[Entity]:
        """Search entities by name (simple contains search)."""
        query_lower = query.lower()
        results = []

        for entity in self._entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue

            if query_lower in entity.name.lower():
                results.append(entity)

            if len(results) >= limit:
                break

        return results

    @property
    def entity_count(self) -> int:
        """Get number of entities."""
        return len(self._entities)

    @property
    def relationship_count(self) -> int:
        """Get number of relationships."""
        return len(self._relationships)
