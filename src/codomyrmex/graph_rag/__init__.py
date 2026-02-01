"""
Graph RAG Module

Knowledge graph-enhanced RAG with entity relationships.
"""

__version__ = "0.1.0"

import hashlib
from typing import Optional, List, Dict, Any, Set, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import threading


class EntityType(Enum):
    """Types of entities in the knowledge graph."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    CONCEPT = "concept"
    EVENT = "event"
    DOCUMENT = "document"
    CUSTOM = "custom"


class RelationType(Enum):
    """Types of relationships in the knowledge graph."""
    IS_A = "is_a"
    PART_OF = "part_of"
    RELATED_TO = "related_to"
    AUTHORED_BY = "authored_by"
    LOCATED_IN = "located_in"
    OCCURRED_ON = "occurred_on"
    REFERENCES = "references"
    CUSTOM = "custom"


@dataclass
class Entity:
    """An entity in the knowledge graph."""
    id: str
    name: str
    entity_type: EntityType = EntityType.CONCEPT
    properties: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    
    @property
    def key(self) -> str:
        """Get unique key for this entity."""
        return f"{self.entity_type.value}:{self.id}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type.value,
            "properties": self.properties,
        }


@dataclass
class Relationship:
    """A relationship between entities."""
    source_id: str
    target_id: str
    relation_type: RelationType
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    
    @property
    def key(self) -> str:
        """Get unique key for this relationship."""
        return f"{self.source_id}-{self.relation_type.value}->{self.target_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "properties": self.properties,
            "weight": self.weight,
        }


@dataclass
class GraphContext:
    """Context retrieved from the knowledge graph."""
    query: str
    entities: List[Entity]
    relationships: List[Relationship]
    paths: List[List[str]] = field(default_factory=list)
    confidence: float = 1.0
    
    @property
    def entity_names(self) -> List[str]:
        """Get names of all entities."""
        return [e.name for e in self.entities]
    
    def to_text(self) -> str:
        """Convert to text representation for LLM context."""
        lines = ["Knowledge Graph Context:"]
        
        if self.entities:
            lines.append("\nEntities:")
            for e in self.entities:
                props = ", ".join(f"{k}={v}" for k, v in e.properties.items())
                lines.append(f"  - {e.name} ({e.entity_type.value}){': ' + props if props else ''}")
        
        if self.relationships:
            lines.append("\nRelationships:")
            for r in self.relationships:
                lines.append(f"  - {r.source_id} --[{r.relation_type.value}]--> {r.target_id}")
        
        return "\n".join(lines)


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
        self._entities: Dict[str, Entity] = {}
        self._relationships: List[Relationship] = []
        self._adjacency: Dict[str, List[str]] = {}  # source_id -> [target_ids]
        self._reverse_adjacency: Dict[str, List[str]] = {}  # target_id -> [source_ids]
        self._lock = threading.Lock()
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the graph."""
        with self._lock:
            self._entities[entity.id] = entity
            if entity.id not in self._adjacency:
                self._adjacency[entity.id] = []
            if entity.id not in self._reverse_adjacency:
                self._reverse_adjacency[entity.id] = []
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
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
    ) -> List[Entity]:
        """Get neighboring entities."""
        neighbor_ids: Set[str] = set()
        
        if direction in ["out", "both"]:
            neighbor_ids.update(self._adjacency.get(entity_id, []))
        
        if direction in ["in", "both"]:
            neighbor_ids.update(self._reverse_adjacency.get(entity_id, []))
        
        return [self._entities[nid] for nid in neighbor_ids if nid in self._entities]
    
    def get_relationships(
        self,
        entity_id: str,
        direction: str = "both",
    ) -> List[Relationship]:
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
    ) -> Optional[List[str]]:
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
        entity_ids: List[str],
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
        entity_type: Optional[EntityType] = None,
        limit: int = 10,
    ) -> List[Entity]:
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


class GraphRAGPipeline:
    """
    RAG pipeline enhanced with knowledge graph context.
    
    Usage:
        pipeline = GraphRAGPipeline(
            graph=knowledge_graph,
            embedding_fn=embed_function,
        )
        
        # Query with graph context
        context = pipeline.retrieve("Who is the CEO of Anthropic?")
        
        # Use context for generation
        print(context.to_text())
    """
    
    def __init__(
        self,
        graph: KnowledgeGraph,
        embedding_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
    ):
        self.graph = graph
        self.embedding_fn = embedding_fn
    
    def extract_entities(self, query: str) -> List[str]:
        """Extract entity IDs mentioned in query (simple word matching)."""
        query_words = set(query.lower().split())
        matches = []
        
        for entity in self.graph._entities.values():
            name_words = set(entity.name.lower().split())
            if name_words & query_words:
                matches.append(entity.id)
        
        return matches
    
    def retrieve(
        self,
        query: str,
        max_entities: int = 10,
        include_neighbors: bool = True,
        max_depth: int = 2,
    ) -> GraphContext:
        """
        Retrieve graph context for a query.
        
        Args:
            query: Search query
            max_entities: Maximum entities to include
            include_neighbors: Whether to include related entities
            max_depth: Max depth for neighbor expansion
            
        Returns:
            GraphContext with entities and relationships
        """
        # Find matching entities
        entity_ids = self.extract_entities(query)
        
        # Also do text search
        for entity in self.graph.search_entities(query, limit=5):
            if entity.id not in entity_ids:
                entity_ids.append(entity.id)
        
        # Expand to neighbors
        all_entity_ids = set(entity_ids[:max_entities])
        if include_neighbors:
            for eid in list(all_entity_ids):
                for neighbor in self.graph.get_neighbors(eid):
                    all_entity_ids.add(neighbor.id)
                    if len(all_entity_ids) >= max_entities:
                        break
        
        # Get entities
        entities = [
            self.graph.get_entity(eid) 
            for eid in all_entity_ids 
            if self.graph.get_entity(eid)
        ]
        
        # Get relationships between these entities
        relationships = []
        for r in self.graph._relationships:
            if r.source_id in all_entity_ids and r.target_id in all_entity_ids:
                relationships.append(r)
        
        return GraphContext(
            query=query,
            entities=entities,
            relationships=relationships,
        )
    
    def combine_context(
        self,
        graph_context: GraphContext,
        text_context: str,
    ) -> str:
        """Combine graph and text context for LLM."""
        return f"""{graph_context.to_text()}

Document Context:
{text_context}"""


__all__ = [
    # Enums
    "EntityType",
    "RelationType",
    # Data classes
    "Entity",
    "Relationship",
    "GraphContext",
    # Core
    "KnowledgeGraph",
    "GraphRAGPipeline",
]
