# Graph RAG Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Graph RAG module provides knowledge graph-enhanced Retrieval-Augmented Generation (RAG) with entity relationships for Codomyrmex. It combines a thread-safe in-memory knowledge graph with a RAG pipeline that leverages entity and relationship context to produce richer, more structured LLM inputs. The module supports entity management, relationship tracking, graph traversal (BFS shortest path, neighbor expansion, subgraph extraction), and context generation for LLM consumption.

## Key Features

- **Knowledge Graph**: Thread-safe in-memory graph with entities, relationships, adjacency tracking, and reverse adjacency
- **Entity Types**: Typed entities (PERSON, ORGANIZATION, LOCATION, CONCEPT, EVENT, DOCUMENT, CUSTOM) with property maps and optional embeddings
- **Relationship Types**: Typed relationships (IS_A, PART_OF, RELATED_TO, AUTHORED_BY, LOCATED_IN, OCCURRED_ON, REFERENCES, CUSTOM) with weights
- **Graph Traversal**: BFS shortest path finding, neighbor expansion (in/out/both directions), and subgraph extraction
- **Entity Search**: Simple text-based entity search with optional type filtering and result limits
- **RAG Pipeline**: `GraphRAGPipeline` that extracts entities from queries, retrieves graph context, and combines it with document context
- **Context Generation**: `GraphContext` with structured text output suitable for LLM prompt augmentation

## Key Components

| Component | Description |
|-----------|-------------|
| `EntityType` | Enum of entity types: PERSON, ORGANIZATION, LOCATION, CONCEPT, EVENT, DOCUMENT, CUSTOM |
| `RelationType` | Enum of relationship types: IS_A, PART_OF, RELATED_TO, AUTHORED_BY, LOCATED_IN, OCCURRED_ON, REFERENCES, CUSTOM |
| `Entity` | Dataclass representing a graph entity with ID, name, type, properties, and optional embedding |
| `Relationship` | Dataclass representing a directed relationship between entities with type, properties, and weight |
| `GraphContext` | Dataclass holding retrieved entities, relationships, and paths with `to_text()` for LLM context |
| `KnowledgeGraph` | Thread-safe in-memory knowledge graph with entity/relationship CRUD, neighbor queries, BFS path finding, subgraph extraction, and entity search |
| `GraphRAGPipeline` | RAG pipeline that extracts entities from queries, expands through the graph, and returns structured `GraphContext` |

## Quick Start

```python
from codomyrmex.graph_rag import (
    KnowledgeGraph, GraphRAGPipeline,
    Entity, Relationship, EntityType, RelationType,
)

# Build a knowledge graph
graph = KnowledgeGraph()
graph.add_entity(Entity(id="python", name="Python", entity_type=EntityType.CONCEPT))
graph.add_entity(Entity(id="ai", name="Artificial Intelligence", entity_type=EntityType.CONCEPT))
graph.add_relationship(Relationship(
    source_id="python",
    target_id="ai",
    relation_type=RelationType.RELATED_TO,
))

# Query neighbors
related = graph.get_neighbors("python")

# Use the RAG pipeline
pipeline = GraphRAGPipeline(graph=graph)
context = pipeline.retrieve("Tell me about Python and AI")
print(context.to_text())
```

### Combining with Document Context

```python
graph_context = pipeline.retrieve("Python programming")
full_context = pipeline.combine_context(graph_context, "Python is a programming language...")
# Use full_context as LLM prompt input
```

## Related Modules

- [llm](../llm/) - LLM infrastructure that consumes graph-enhanced context
- [documentation](../documentation/) - Document sources that feed into the knowledge graph

## Navigation

- **Source**: [src/codomyrmex/graph_rag/](../../../src/codomyrmex/graph_rag/)
- **API Specification**: [src/codomyrmex/graph_rag/API_SPECIFICATION.md](../../../src/codomyrmex/graph_rag/API_SPECIFICATION.md)
- **Parent**: [docs/modules/](../README.md)
