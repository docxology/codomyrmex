# Graph RAG Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

Knowledge graph-enhanced RAG with entity relationships.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **THINK** | Knowledge graph reasoning over entity relationships | Direct Python import |
| **OBSERVE** | Query graph knowledge base for contextual retrieval | Direct Python import |
| **LEARN** | Update knowledge graph with new entities and relationships | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. The Architect agent queries the KnowledgeGraph during THINK for relationship-aware reasoning, and agents update the graph during LEARN to capture new domain knowledge.

## Key Exports

### Classes

- **`EntityType`** — Types of entities in the knowledge graph.
- **`RelationType`** — Types of relationships in the knowledge graph.
- **`Entity`** — An entity in the knowledge graph.
- **`Relationship`** — A relationship between entities.
- **`GraphContext`** — Context retrieved from the knowledge graph.
- **`KnowledgeGraph`** — In-memory knowledge graph for entity and relationship storage.
- **`GraphRAGPipeline`** — RAG pipeline enhanced with knowledge graph context.

## Quick Start

```python
from codomyrmex.graph_rag import (
    KnowledgeGraph, Entity, Relationship, EntityType, RelationType,
    GraphRAGPipeline, GraphContext
)

# Build knowledge graph
graph = KnowledgeGraph()

# Add entities
graph.add_entity(Entity(id="python", name="Python", entity_type=EntityType.CONCEPT))
graph.add_entity(Entity(id="ai", name="Artificial Intelligence", entity_type=EntityType.CONCEPT))
graph.add_entity(Entity(id="ml", name="Machine Learning", entity_type=EntityType.CONCEPT))

# Add relationships
graph.add_relationship(Relationship(
    source_id="ml",
    target_id="ai",
    relation_type=RelationType.PART_OF
))
graph.add_relationship(Relationship(
    source_id="python",
    target_id="ml",
    relation_type=RelationType.RELATED_TO
))

# Query graph
neighbors = graph.get_neighbors("python")
path = graph.find_path("python", "ai")
```

## RAG Pipeline

```python
# Create pipeline
pipeline = GraphRAGPipeline(graph=graph)

# Retrieve context for query
context = pipeline.retrieve("What programming languages are used in AI?")

# Use in LLM prompt
print(context.to_text())
# Knowledge Graph Context:
# Entities:
#   - Python (concept)
#   - Machine Learning (concept)
# Relationships:
## Directory Structure
- `models.py` — Data models (Entity, Relationship, GraphContext, etc.)
- `graph.py` — Knowledge graph implementation (KnowledgeGraph)
- `pipeline.py` — RAG pipeline logic (GraphRAGPipeline)
- `__init__.py` — Public API re-exports

## Exports

| Class | Description |
| :--- | :--- |
| `KnowledgeGraph` | Entity and relationship storage |
| `Entity` | Node with id, name, type, properties |
| `Relationship` | Edge with source, target, type, weight |
| `EntityType` | Enum: person, organization, location, concept, etc. |
| `RelationType` | Enum: is_a, part_of, related_to, authored_by, etc. |
| `GraphRAGPipeline` | Query graph for LLM context |
| `GraphContext` | Retrieved entities and relationships |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k graph_rag -v
```

## Documentation

- [Module Documentation](../../../docs/modules/graph_rag/README.md)
- [Agent Guide](../../../docs/modules/graph_rag/AGENTS.md)
- [Specification](../../../docs/modules/graph_rag/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
