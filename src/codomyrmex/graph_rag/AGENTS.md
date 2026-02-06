# Agent Guidelines - Graph RAG

## Module Overview

Knowledge graph-enhanced RAG with entity relationships and traversal.

## Key Classes

- **KnowledgeGraph** — Entity and relationship storage
- **Entity** — Node with id, name, type, properties
- **Relationship** — Edge with source, target, type, weight
- **EntityType** — Enum: person, organization, location, concept, etc.
- **RelationType** — Enum: is_a, part_of, related_to, authored_by, etc.
- **GraphRAGPipeline** — Query graph for LLM context

## Agent Instructions

1. **Build graph incrementally** — Add entities and relationships as discovered
2. **Use typed entities** — Set `EntityType` for better traversal
3. **Weight relationships** — Higher weight = stronger connection
4. **Query multi-hop** — Use path finding for indirect relationships
5. **Combine with text** — Use graph context alongside text retrieval

## Common Patterns

```python
from codomyrmex.graph_rag import (
    KnowledgeGraph, Entity, Relationship, EntityType, RelationType
)

graph = KnowledgeGraph()

# Build knowledge graph
graph.add_entity(Entity(id="python", name="Python", entity_type=EntityType.CONCEPT))
graph.add_entity(Entity(id="ml", name="Machine Learning", entity_type=EntityType.CONCEPT))
graph.add_relationship(Relationship(
    source_id="python", target_id="ml", relation_type=RelationType.USED_FOR
))

# Query neighbors
neighbors = graph.get_neighbors("python")

# Find paths
path = graph.find_path("python", "ml")
```

## Testing Patterns

```python
# Verify graph operations
graph = KnowledgeGraph()
graph.add_entity(Entity(id="a", name="A", entity_type=EntityType.CONCEPT))
graph.add_entity(Entity(id="b", name="B", entity_type=EntityType.CONCEPT))
graph.add_relationship(Relationship("a", "b", RelationType.RELATED_TO))

assert len(graph.get_neighbors("a")) == 1
assert graph.get_entity("a").name == "A"
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
