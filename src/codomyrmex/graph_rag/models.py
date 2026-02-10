"""
Graph RAG Models

Data classes and enums for knowledge graph-enhanced RAG.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


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
    properties: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None

    @property
    def key(self) -> str:
        """Get unique key for this entity."""
        return f"{self.entity_type.value}:{self.id}"

    def to_dict(self) -> dict[str, Any]:
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
    properties: dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0

    @property
    def key(self) -> str:
        """Get unique key for this relationship."""
        return f"{self.source_id}-{self.relation_type.value}->{self.target_id}"

    def to_dict(self) -> dict[str, Any]:
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
    entities: list[Entity]
    relationships: list[Relationship]
    paths: list[list[str]] = field(default_factory=list)
    confidence: float = 1.0

    @property
    def entity_names(self) -> list[str]:
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
